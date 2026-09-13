"""
HealthConnect AI - Prompt Templates
# ====================================
Reusable prompt templates for various AI operations.

Template types:
- RAG prompts (retrieval-augmented generation)
- Safety prompts (safety classification)
- Intent prompts (intent classification)
- Summarization prompts
- Feedback prompts
"""

from typing import Dict, List, Optional, Any
from string import Template


class PromptTemplate:
    """Base prompt template class"""
    
    def __init__(self, template: str):
        self.template = Template(template)
    
    def render(self, **kwargs) -> str:
        """Render template with variables"""
        return self.template.safe_substitute(**kwargs)
    
    def __str__(self) -> str:
        return self.template.template


class RAGPromptTemplate:
    """RAG pipeline prompt templates"""
    
    SYSTEM_PROMPT = """You are the HealthConnect AI Assistant. Answer the user's question based ONLY on the provided context.

SAFETY RULES:
1. Only use information from the provided context
2. If the answer is not in the context, say "I don't have this information"
3. Never provide medical advice
4. Always cite your sources

Context:
{context}

User Query: {query}

Instructions:
1. Answer based ONLY on the context above
2. Be concise and helpful
3. Include source citations where possible
4. If information is not found, acknowledge this clearly
5. Do not invent or speculate
"""
    
    HYBRID_PROMPT = """You are the HealthConnect AI Assistant. Use the provided context to answer the user's question.

Context (from {num_chunks} sources):
{context}

Conversation History:
{history}

User Query: {query}

Response Guidelines:
- Ground your answer in the provided context
- Acknowledge uncertainty when present
- Provide helpful next steps
- Maintain professional tone

Answer:
"""
    
    CITATION_PROMPT = """Based on the context below, answer the user's query with proper citations.

Context:
{context}

Query: {query}

Requirements:
1. Answer the query accurately
2. Cite sources using [Source: chunk_id]
3. If no relevant information, state this clearly
4. Do not add information beyond the context

Answer:
"""


class SafetyPromptTemplate:
    """Safety classification prompt templates"""
    
    CLASSIFICATION_PROMPT = """You are a safety classifier for the HealthConnect AI Assistant. Classify the following user query into one of these safety categories:

Categories:
1. safe - Normal administrative query
2. medical_advice_request - Asking for medical advice
3. emergency - Medical emergency
4. prescription_request - Medication refill requests
5. test_result_query - Test result interpretation
6. out_of_scope - Completely unrelated
7. pii_request - Requesting personal information
8. abusive_language - Abusive or inappropriate

User Query: {query}

Respond in JSON format:
{
    "safety_category": "category_name",
    "action": "allow|block|emergency_protocol|escalate|redirect",
    "confidence": 0.0-1.0,
    "risk_score": 0-100,
    "reasoning": "Brief explanation"
}
"""

VERIFICATION_PROMPT = """Verify whether the following AI response is safe and appropriate.

User Query: {query}

AI Response: {response}

Check for:

Medical advice provision

Emergency mishandling

Information hallucination

Privacy violations

Inappropriate content

Respond in JSON:
{
    "is_safe": true/false,
    "issues_found": ["issue1", "issue2"],
    "severity": "none|low|medium|high|critical",
    "action": "allow|block|regenerate|escalate"
}
"""

class IntentPromptTemplate:
    """Intent classification prompt templates"""

    CLASSIFICATION_PROMPT = """Classify the following user query into the correct intent category.

Intent Categories:

appointment_booking - Booking a new appointment

appointment_reschedule - Changing appointment time

appointment_cancel - Canceling appointment

clinic_information - Location, hours, services

billing_query - Costs, payments, billing

insurance_query - Insurance coverage

preparation_guidance - Preparing for appointment

policy_query - Clinic policies

general_faq - General questions

medical_advice_request - Medical advice

emergency - Medical emergency

escalation_request - Want human assistance

feedback - Providing feedback

out_of_scope - Unrelated query

User Query: {query}

Respond in JSON:
{
    "intent": "intent_category",
    "confidence": 0.0-1.0,
    "routing": "target_service",
    "alternative_intents": ["other_possible_intents"]
}
"""

    ROUTING_PROMPT = """Route the following query to the appropriate service based on its intent.

User Query: {query}
Detected Intent: {intent}

Available Services:

appointment_service (booking, rescheduling, cancellation)

knowledge_base (clinic info, policies, FAQs)

billing_service (billing, payments)

insurance_service (insurance verification)

safety_protocol (medical advice, safety concerns)

emergency_protocol (emergencies)

escalation_service (human assistance)

feedback_service (feedback collection)

redirect_service (out of scope)

Respond with the routing decision:
{
    "service": "service_name",
    "priority": "normal|high|critical",
    "needs_escalation": false,
    "reasoning": "Brief explanation"
}
"""


class SummaryPromptTemplate:
    """Conversation summary prompt templates"""

    CONVERSATION_SUMMARY = """Summarize the following conversation between a patient and the HealthConnect AI Assistant.

Conversation:
{conversation}

Summarize:

User's primary need

Information provided

Actions taken

Escalations made

Follow-up required

Summary:
"""

    ACTION_SUMMARY = """Extract all actions taken during this conversation.

Conversation:
{conversation}

Extract:

Appointment actions (booked, rescheduled, cancelled)

Information queries answered

Escalations created

Notifications sent

Pending follow-ups

Actions:
"""

