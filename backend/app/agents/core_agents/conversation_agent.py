"""
HealthConnect AI - Conversation Agent (Production Ready)
=========================================================
Generates responses using Groq with RAG context.
"""

import time
import os
import requests
from typing import List, Dict, Any, Optional

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)
from app.rag.context_builder import ContextBuilder
from app.rag.citation_generator import CitationGenerator

from config.logging_config import get_logger
from config.prompts.system_prompts import CONVERSATION_AGENT_PROMPT
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

_SHORT_FOLLOWUPS = {
    "yes", "yep", "yeah", "yup", "sure", "ok", "okay", "k",
    "no", "nope", "nah", "n",
    "please", "please do", "go ahead", "yes please",
    "sounds good", "alright", "fine",
}


def _is_short_followup(query: str) -> bool:
    if not query:
        return False
    q = query.strip().lower().rstrip(".!?,")
    return q in _SHORT_FOLLOWUPS


_STRUCTURED_MARKERS = ("Variable:", "Data Type:", "Description:", "Example:", "Notes:")


def _looks_like_structured_leak(text: str) -> bool:
    """Detect raw data-dictionary rows leaking into a chat response."""
    if not text:
        return False
    return sum(1 for m in _STRUCTURED_MARKERS if m in text) >= 2


class ConversationAgent(BaseAgent):
    """Conversation Agent using Groq for response generation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.CONVERSATION, config)
        self.context_builder = ContextBuilder()
        self.citation_generator = CitationGenerator()
        self.max_history_messages = 10
        
        # Groq configuration
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        logger.info(f"ConversationAgent initialized with Groq model: {self.model}")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Generate response using Groq with RAG context."""
        start_time = time.time()
        
        # Build context from retrieved chunks
        built_context = self.context_builder.build_context(
            self._convert_chunks_to_results(context.retrieved_chunks),
            include_citations=True,
        )
        
        logger.info(f"Context: {built_context.chunks_used} chunks, {len(built_context.context_text)} chars")
        
        # Generate response
        response_text = await self._generate_with_groq(context, built_context)
        
        # Generate citations
        citations = self.citation_generator.generate_citations(built_context.sources)
        
        execution_time = (time.time() - start_time) * 1000
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "response": response_text,
                "citations": citations,
                "context_used": built_context.context_text,
                "sources": built_context.sources,
            },
            confidence=0.7 if built_context.chunks_used > 0 else 0.3,
            execution_time_ms=execution_time,
        )
    
    async def _generate_with_groq(self, context: AgentContext, built_context: Any) -> str:
        """Generate response using Groq API directly."""
        if not self.api_key:
            logger.warning("No Groq API key available")
            return self._generate_fallback(context, built_context)
        
        # Build context text (limit to 2000 chars)
        context_text = built_context.context_text[:2000] if built_context.context_text else "No specific context available."
        
        # Build system prompt
        system_prompt = """You are HealthConnect AI Assistant, a warm and professional clinic assistant.

STRICT GROUNDING RULES:
1. Answer using (a) the Knowledge Base context AND (b) the "Context from prior
   conversation" block above it. The prior-conversation block contains verified
   facts this user has shared with us (name, preferences, allergies) and is
   authoritative for questions about the user themselves.
2. Do NOT use general medical knowledge, your training data, or your own opinion.
3. Do NOT invent clinic details, doctor names, prices, policies, or medical advice.
4. Never diagnose, prescribe, or recommend medications.
5. If the user ASKS about themselves ("what is my name", "what am I allergic to",
   "what did I say"), answer directly from the prior-conversation facts. If the
   fact isn't there, say so plainly.
   BUT if the user is just TELLING you something about themselves (an introduction,
   a preference, an allergy, an email), simply acknowledge it warmly and continue
   the conversation naturally - do NOT answer as if you were asked.
   Never say "I don't have that information in the prior conversation" when the
   user is the one providing the information.

WHEN THE ANSWER IS NOT CLEARLY IN THE CONTEXT, pick the RIGHT response shape:

A) If the user's question is about CLINIC LOGISTICS (hours, days, services, location,
   booking process, insurance, cancellations) and the answer might be implied by the
   context even if not verbatim:
    Answer helpfully using the closest matching information from the context.
    Example: "Can I come Saturday morning?"  answer with Saturday hours from KB.

B) If the user is describing a MEDICAL SITUATION that sounds urgent, time-sensitive,
   or possibly an emergency (labor, chest pain, severe symptoms, injury, sudden
   deterioration, etc.):
    Do NOT use the out-of-scope template.
    Respond like this:
     "That sounds like it may need urgent care. Please call HealthConnect Clinic
      directly during opening hours, or call 911 / 999 / 112 if it's an emergency.
      I can also help you book the earliest available appointment  would you like that?"

C) Only if the question is TRULY OUT OF SCOPE (unrelated topic, another disease not
   handled here, or asking for information not in the KB and not implied by it):
    Respond with:
     "I don't have details about that in HealthConnect's knowledge base. I can
      connect you with a HealthConnect staff member, or help you book a consultation.
      Which would you prefer?"

DO NOT say "doesn't cover [topic]" for anything that is actually about clinic hours,
services, or booking  those are in scope. Only use shape C for genuinely unrelated
or unanswerable topics.

TONE:
- Warm, clear, and concise.
- Never lead with "I can't"  lead with what you CAN do (book a consultation, share clinic info, help with appointments).
- Never phrase a response as "doesn't cover [thing]" for things that are actually
  in scope (hours, days, services, booking). Only use that phrasing for genuinely
  unrelated topics.
- If a user describes a time-sensitive or urgent medical situation, direct them
  to the clinic or emergency services FIRST  do not lead with a polite refusal.
- Keep answers under 120 words unless the user asks for detail."""
        
        # Build conversation history text (last 4 turns, most recent last)
        history_text = ""
        try:
            hist = getattr(context, "history", None) or []
            recent = hist[-4:]
            if recent:
                lines = []
                for m in recent:
                    role = (m.get("role") or "user").upper()
                    content = (m.get("content") or "").strip()
                    if content:
                        lines.append(f"{role}: {content}")
                history_text = "\n".join(lines)
        except Exception as e:
            logger.warning(f"Failed to format history: {e}")
            history_text = ""

        # If this is a short follow-up (yes/no/sure), the answer MUST be
        # grounded in the previous assistant turn.
        # If this is a short follow-up (yes/no/sure), the answer MUST be
        # grounded in the previous assistant turn.
        if _is_short_followup(context.query):
            followup_note = (
                "CRITICAL INSTRUCTION: The user's message is a short follow-up "
                f"({context.query!r}). Look at the LAST assistant message above "
                "and decide what the user is agreeing to.\n\n"
                "If the last assistant message was an OFFER "
                "(e.g. 'would you like to book?'), confirm and continue the flow.\n\n"
                "If the last assistant message was a REQUEST FOR DETAILS "
                "(e.g. 'what date and time?'), the user's 'yes' does not answer "
                "that. Politely re-ask for the needed details.\n\n"
                "Your response MUST:\n"
                "1. NOT use an out-of-scope template.\n"
                "2. NOT say 'doesn't cover that topic'.\n"
                "3. NOT output raw KB content.\n"
                "4. Stay in the flow of what the user is trying to do.\n\n"
            )
        else:
            followup_note = ""

        # Prefer the memory block assembled by chat_service (summary + facts)
        memory_block = (getattr(context, "metadata", None) or {}).get("memory_block") or ""

        if memory_block:
            history_block = f"Context from prior conversation:\n{memory_block}\n\n"
        else:
            history_block = (
                f"Recent conversation:\n{history_text}\n\n"
                if history_text else ""
            )

        # Build user prompt with context.
        # Order matters: KB first, then memory (memory is most recent signal),
        # then the current question.
        user_prompt = f"""{followup_note}Knowledge Base context:
{context_text}

{history_block}User question: {context.query}

Answer using the Knowledge Base for clinic facts and the prior-conversation
block (if present) for facts about the user. If the user's question is about
themselves and the answer is not in the prior-conversation block, say so plainly.
Be concise and helpful."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 600,
            "temperature": 0.3,
        }
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Run in thread executor to avoid blocking
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                if _looks_like_structured_leak(content):
                    logger.warning("Structured-data leak detected; using safe template")
                    return (
                        "HealthConnect's assistant doesn't cover that topic. "
                        "For any concern about a specific condition, please:\n\n"
                        "\u2022 Book a consultation with a HealthConnect clinician\n"
                        "\u2022 In an emergency, call 911 / 999 / 112 immediately\n\n"
                        "Would you like help booking an appointment?"
                    )
                
                if content and content.strip():
                    logger.info(f"Groq response generated: {len(content)} chars")
                    return content.strip()
                else:
                    logger.warning("Groq returned empty content")
                    return self._generate_fallback(context, built_context)
            else:
                logger.warning(f"Groq API error: {response.status_code} - {response.text[:200]}")
                return self._generate_fallback(context, built_context)
                
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return self._generate_fallback(context, built_context)
    
    def _generate_fallback(self, context: AgentContext, built_context: Any) -> str:
        """Generate fallback response using context."""
        if built_context.chunks_used > 0:
            # Extract relevant text from context
            extracted = self._extract_answer_from_context(context.query, built_context.context_text)
            if extracted and extracted.strip():
                return extracted

        # No useful context  patient-friendly out-of-scope response
        return (
            "HealthConnect's assistant doesn't cover that topic. For any concern "
            "about a specific condition, please:\n\n"
            "\u2022 Book a consultation with a HealthConnect clinician\n"
            "\u2022 In an emergency, call 911 / 999 / 112 immediately\n\n"
            "Would you like help booking an appointment?"
        )
    
    def _extract_answer_from_context(self, query: str, context: str) -> str:
        """Extract answer from context using text overlap (with leak guard)."""
        if not context:
            return (
                "I don't have a confident answer for that in HealthConnect's "
                "knowledge base. I can connect you with a staff member or help "
                "you book a consultation. Which would you prefer?"
            )

        sentences = context.split('\n')
        query_terms = set(query.lower().split())

        scored_sentences = []
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            # Skip structured data / KB artefacts / headers
            if _looks_like_structured_leak(s):
                continue
            if s.startswith(("Q:", "A:", "Variable:", "Notes:", "Example:")):
                continue
            if s.startswith(tuple(f"{i}." for i in range(1, 30))):
                continue
            sentence_terms = set(s.lower().split())
            overlap = query_terms.intersection(sentence_terms)
            if overlap:
                scored_sentences.append((len(overlap), s))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        if scored_sentences:
            top = [s for _, s in scored_sentences[:3] if len(s) > 20]
            joined = ' '.join(top)
            if joined.strip() and not _looks_like_structured_leak(joined):
                return joined

        return (
            "I don't have a confident answer for that in HealthConnect's "
            "knowledge base. I can connect you with a staff member or help "
            "you book a consultation. Which would you prefer?"
        )
    
    def _convert_chunks_to_results(self, chunks: List[Dict[str, Any]]) -> List[Any]:
        """Convert chunk dictionaries to retrieval results."""
        from app.rag.retriever import RetrievalResult
        
        results = []
        for chunk in chunks:
            results.append(RetrievalResult(
                chunk_id=chunk.get("chunk_id", ""),
                text=chunk.get("text", ""),
                score=chunk.get("score", 0.5),
                retrieval_method=chunk.get("retrieval_method", "hybrid"),
                metadata=chunk.get("metadata", {}),
            ))
        
        return results
