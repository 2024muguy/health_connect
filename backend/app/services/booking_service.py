"""
HealthConnect AI - Conversational Booking Service (Hybrid)
===========================================================
Collects booking slots via chat, confirms, then calls the existing
appointment API. Uses a per-session slot state machine.

Slots: service, date, time, patient_name, confirmed

Flow:
    user says "book me" -> assistant asks for service
    user provides service -> assistant asks for date
    ... -> assistant asks for time -> assistant asks to confirm
    user confirms -> service calls AppointmentService.create_appointment
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ============================================================
# Slot state
# ============================================================

@dataclass
class BookingSlots:
    service: Optional[str] = None
    date: Optional[str] = None       # YYYY-MM-DD
    time: Optional[str] = None       # HH:MM
    location: Optional[str] = None   # "Central" | "Lakeside"
    contact_method: Optional[str] = None  # "email" | "phone"
    patient_name: Optional[str] = None
    confirmed: bool = False
    attempts: int = 0
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())

    def missing(self) -> list[str]:
        m = []
        if not self.service: m.append("service")
        if not self.date: m.append("date")
        if not self.time: m.append("time")
        return m

    def complete(self) -> bool:
        return not self.missing()


# ============================================================
# BookingService
# ============================================================

_EXTRACT_SYSTEM = (
    "Extract appointment slot values from the user's message. Return ONLY "
    "valid JSON with any of these keys that are present:\n"
    "  service (string — pick the closest match from: General, Follow-up, "
    "Specialist, Laboratory, Imaging, Vaccination, Physical, Consultation, "
    "Urgent Care, Telehealth),\n"
    "  date (YYYY-MM-DD), time (HH:MM 24-hour),\n"
    "  location (Central or Lakeside),\n"
    "  contact_method (email or phone),\n"
    "  patient_name (string), confirmed (bool)\n"
    "Omit keys not present. No prose, no code fences."
)

_ASK = {
    "service": "What kind of appointment would you like? (e.g. General, Follow-up, Specialist, Laboratory)",
    "date":    "What date works for you? (YYYY-MM-DD)",
    "time":    "What time works best? (e.g. 09:00 or 14:30)",
    "confirm": "Just to confirm: {service} on {date} at {time}. Shall I book it?",
}


class BookingService:
    """Hybrid conversational booking."""

    def __init__(self) -> None:
        self.enabled = settings.booking.ENABLED
        self.auto_confirm = settings.booking.AUTO_CONFIRM
        self.max_attempts = settings.booking.MAX_SLOT_ATTEMPTS
        self.model = settings.groq.BOOKING_MODEL
        self.api_key = settings.groq.API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # session_token -> BookingSlots
        self._sessions: Dict[str, BookingSlots] = {}

    # -------------------- public --------------------

    def is_active(self, session_token: str) -> bool:
        return session_token in self._sessions

    def start(self, session_token: str) -> BookingSlots:
        slots = BookingSlots()
        self._sessions[session_token] = slots
        return slots

    def get(self, session_token: str) -> Optional[BookingSlots]:
        return self._sessions.get(session_token)

    def cancel(self, session_token: str) -> None:
        self._sessions.pop(session_token, None)

    @staticmethod
    def detect_booking_intent(message: str) -> bool:
        """Heuristic: does the message read as a booking request?

        Broad trigger set so a wide variety of natural phrasings work:
          "I want to book", "book me in", "book for me", "make an appointment",
          "schedule a visit", "reserve a slot", "I'd like to see a doctor",
          "can you book", "I want to visit ... book", "please book"
        """
        if not message:
            return False
        m = message.lower()

        strong_phrases = (
            "book", "booking",
            "make an appointment", "schedule an appointment",
            "reserve an appointment", "reserve a slot",
            "schedule a visit", "book a visit",
            "make a booking", "arrange an appointment",
        )
        if any(p in m for p in strong_phrases):
            return True

        weak_phrases = ("appointment", "visit", "consultation", "see a doctor", "see a clinician")
        intent_verbs = ("want", "need", "like", "please", "help")
        if any(w in m for w in weak_phrases) and any(v in m for v in intent_verbs):
            return True

        return False

    def update_from_message(
        self,
        session_token: str,
        message: str,
        existing_slots: Optional[BookingSlots] = None,
    ) -> BookingSlots:
        slots = existing_slots or self._sessions.get(session_token) or self.start(session_token)
        extracted = self._extract(message)
        for k, v in (extracted or {}).items():
            if v in (None, "", []):
                continue
            setattr(slots, k, v)
        self._sessions[session_token] = slots
        return slots

    def next_prompt(self, slots: BookingSlots) -> str:
        missing = slots.missing()
        if missing:
            return _ASK[missing[0]]
        return _ASK["confirm"].format(
            service=slots.service, date=slots.date, time=slots.time
        )

    def ready_to_book(self, slots: BookingSlots) -> bool:
        return slots.complete() and (slots.confirmed or self.auto_confirm)

    # -------------------- internals --------------------

    def _extract(self, message: str) -> Dict[str, Any]:
        if not self.api_key:
            return self._rule_extract(message)
        try:
            r = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": _EXTRACT_SYSTEM},
                        {"role": "user", "content": message},
                    ],
                    "max_tokens": 150,
                    "temperature": 0.0,
                },
                timeout=15,
            )
            if r.status_code != 200:
                return self._rule_extract(message)
            content = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[BOOKING-LLM] raw: {content[:200]}", flush=True)
            data = self._parse_json(content)
            print(f"[BOOKING-LLM] parsed: {data}", flush=True)
            return data or self._rule_extract(message)
        except Exception as e:
            logger.warning(f"booking extract failed: {e}")
            return self._rule_extract(message)

    def _rule_extract(self, message: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        m = message.lower()

        # explicit date YYYY-MM-DD
        m_date = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", message)
        if m_date:
            out["date"] = m_date.group(1)

        # natural weekday ("saturday", "next monday") -> next occurrence
        if "date" not in out:
            weekdays = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6,
            }
            for name, target_wd in weekdays.items():
                if name in m:
                    from datetime import date as _date, timedelta as _td
                    today = _date.today()
                    days_ahead = (target_wd - today.weekday() + 7) % 7 or 7
                    out["date"] = (today + _td(days=days_ahead)).isoformat()
                    break

        # explicit time HH:MM
        m_time = re.search(r"\b([01]\d|2[0-3]):([0-5]\d)\b", message)
        if m_time:
            out["time"] = f"{m_time.group(1)}:{m_time.group(2)}"

        # natural time like "11 am" / "3 pm"
        m_ampm = re.search(r"\b(\d{1,2})\s*(am|pm)\b", m)
        if m_ampm and "time" not in out:
            hour = int(m_ampm.group(1))
            if m_ampm.group(2) == "pm" and hour < 12:
                hour += 12
            if m_ampm.group(2) == "am" and hour == 12:
                hour = 0
            out["time"] = f"{hour:02d}:00"

        # service keywords
        service_map = [
            ("follow-up", "Follow-up"), ("follow up", "Follow-up"),
            ("general", "General"), ("specialist", "Specialist"),
            ("lab", "Laboratory"), ("laboratory", "Laboratory"),
            ("imaging", "Imaging"), ("scan", "Imaging"),
            ("vaccin", "Vaccination"), ("physical", "Physical"),
            ("consult", "Consultation"), ("urgent", "Urgent Care"),
            ("tele", "Telehealth"), ("virtual", "Telehealth"),
        ]
        for kw, svc in service_map:
            if kw in m:
                out["service"] = svc
                break

        # location
        if "lakeside" in m:
            out["location"] = "Lakeside"
        elif "central" in m:
            out["location"] = "Central"

        # contact
        if "email" in m:
            out["contact_method"] = "email"
        elif "phone" in m or "call" in m or "sms" in m:
            out["contact_method"] = "phone"

        # confirmation
        if re.search(r"\b(yes|confirm|book it|go ahead|sure)\b", message, re.I):
            out["confirmed"] = True

        return out

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        t = re.sub(r"```(?:json)?", "", text).strip("` \n")
        try:
            return json.loads(t)
        except Exception:
            m = re.search(r"\{.*\}", t, re.DOTALL)
            if not m:
                return None
            try:
                return json.loads(m.group(0))
            except Exception:
                return None


booking_service = BookingService()
