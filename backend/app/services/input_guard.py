"""
HealthConnect AI - Input guard.
Detects prompt injection, jailbreak, encoding tricks.
"""
import re
import unicodedata
from typing import Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


class InputGuardResult:
    def __init__(self, allowed: bool, reason: Optional[str] = None,
                 sanitized: Optional[str] = None):
        self.allowed = allowed
        self.reason = reason
        self.sanitized = sanitized


# ---------------- Sanitization ----------------

_ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Unicode homoglyphs commonly used to bypass keyword filters
_HOMOGLYPH_MAP = str.maketrans({
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p",
    "\u0441": "c", "\u0445": "x", "\u0443": "y", "\u04bb": "h",
    "\u0456": "i", "\u0501": "d", "\u0455": "s", "\u04cf": "l",
})


def sanitize(text: str) -> str:
    """Strip invisible chars, normalize unicode, decode common tricks."""
    if not text:
        return ""
    # Unicode normalize (NFKC collapses look-alikes)
    t = unicodedata.normalize("NFKC", text)
    # Replace Cyrillic homoglyphs
    t = t.translate(_HOMOGLYPH_MAP)
    # Remove zero-width + control
    t = _ZERO_WIDTH.sub("", t)
    t = _CONTROL.sub("", t)
    # Collapse excessive whitespace
    t = re.sub(r"\s{3,}", "  ", t)
    return t.strip()


# ---------------- Injection detection ----------------

_INJECTION_PATTERNS = [
    # Instruction overrides
    r"ignore (all )?(previous|prior|above) (instructions|prompts|rules)",
    r"disregard (all )?(previous|prior|above)",
    r"forget (all )?(previous|prior|your) (instructions|rules|prompt)",
    r"override (your )?(system|safety|rules)",
    # System prompt extraction
    r"(reveal|show|print|repeat|echo|output).{0,20}(system prompt|instructions|rules)",
    r"what (is|are) your (system prompt|instructions|rules)",
    r"you (are|were) (programmed|instructed) to",
    # Jailbreaks
    r"\b(DAN|do anything now)\b",
    r"pretend (to be|you are) .{0,20}(doctor|nurse|physician|clinician)",
    r"act as (a |an )?(doctor|nurse|physician|clinician|diagnostic)",
    r"role[- ]?play as .{0,20}(doctor|nurse)",
    r"you are now .{0,20}(unrestricted|uncensored|free)",
    # Safety bypass
    r"bypass (your )?(safety|guardrails|filters|rules)",
    r"(enable|activate) (developer|debug|admin) mode",
    r"sudo .{0,20}(mode|access)",
    # Data exfiltration
    r"(list|show|dump|export) (all )?(patients|users|records|appointments)",
    r"select .{0,20}from .{0,20}(users|patients|appointments)",
    r"drop table|truncate table|delete from",
    # Encoding tricks
    r"(base64|rot13|hex|unicode)\s*[-:]\s*[A-Za-z0-9+/=]{20,}",
    r"decode (this|the following) .{0,20}(base64|rot13)",
    # Tool abuse (SSRF)
    r"(fetch|curl|wget|request|download) (http|https|ftp|file)://",
    r"https?://(localhost|127\.0\.0\.1|169\.254\.|10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.)",
]

_INJECTION_RE = re.compile("|".join(f"(?:{p})" for p in _INJECTION_PATTERNS),
                            re.IGNORECASE | re.DOTALL)


def check_injection(text: str) -> InputGuardResult:
    """Detect prompt injection / jailbreak patterns."""
    if not text:
        return InputGuardResult(True, sanitized="")

    sanitized = sanitize(text)

    # Length cap
    if len(sanitized) > 4000:
        return InputGuardResult(False, reason="message_too_long",
                                sanitized=sanitized[:4000])

    m = _INJECTION_RE.search(sanitized)
    if m:
        logger.warning(f"Injection pattern detected: {m.group(0)[:80]!r}")
        return InputGuardResult(False, reason="injection_detected",
                                sanitized=sanitized)

    return InputGuardResult(True, sanitized=sanitized)


def guard_message(text: str) -> InputGuardResult:
    """Full input guard pipeline."""
    return check_injection(text)
