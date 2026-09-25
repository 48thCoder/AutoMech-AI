from __future__ import annotations

import json
import logging
from typing import Any

from django.conf import settings
import google.generativeai as genai

from api.models import (
    CategoryChoices,
    Conversation,
    Diagnosis,
    MediaUpload,
    SeverityLevel,
)

logger = logging.getLogger(__name__)

RULE_BASED_DIAGNOSES: dict[str, dict[str, str]] = {
    CategoryChoices.ENGINE: {
        "summary": "Engine malfunction detected based on reported symptoms.",
        "probable_cause": "Faulty ignition coils, damaged spark plugs, or cooling system failure.",
        "severity": SeverityLevel.HIGH,
        "suggested_service": "Engine diagnostic scan and cooling system inspection",
        "estimated_cost": "$150–$400",
        "estimated_time": "2–4 hours",
    },
    CategoryChoices.BRAKES: {
        "summary": "Braking system wear or hydraulic pressure irregularity.",
        "probable_cause": "Worn brake pads, warped rotors, or low brake fluid.",
        "severity": SeverityLevel.CRITICAL,
        "suggested_service": "Brake pad and rotor replacement with fluid flush",
        "estimated_cost": "$200–$500",
        "estimated_time": "1–3 hours",
    },
    CategoryChoices.ELECTRICAL: {
        "summary": "Electrical or charging system irregularity.",
        "probable_cause": "Failing alternator, deteriorated battery terminals, or weak 12V battery.",
        "severity": SeverityLevel.MEDIUM,
        "suggested_service": "Battery, starter, and alternator load testing",
        "estimated_cost": "$100–$350",
        "estimated_time": "1–2 hours",
    },
    CategoryChoices.TYRES: {
        "summary": "Tire pressure loss, misalignment, or tread wear.",
        "probable_cause": "Tread wear, puncture damage, or wheel imbalance.",
        "severity": SeverityLevel.MEDIUM,
        "suggested_service": "Wheel alignment, rotation, and tire puncture repair/replacement",
        "estimated_cost": "$50–$250",
        "estimated_time": "1 hour",
    },
    CategoryChoices.AC: {
        "summary": "Climate control cooling or ventilation failure.",
        "probable_cause": "Refrigerant leak, clogged cabin air filter, or failed AC compressor.",
        "severity": SeverityLevel.LOW,
        "suggested_service": "AC evacuation, recharge, and leak inspection",
        "estimated_cost": "$120–$300",
        "estimated_time": "1–2 hours",
    },
    CategoryChoices.TRANSMISSION: {
        "summary": "Transmission shifting or gear engagement degradation.",
        "probable_cause": "Low or contaminated transmission fluid, worn clutch, or torque converter slip.",
        "severity": SeverityLevel.HIGH,
        "suggested_service": "Transmission fluid service and diagnostic scan",
        "estimated_cost": "$250–$700",
        "estimated_time": "3–5 hours",
    },
    CategoryChoices.SUSPENSION: {
        "summary": "Suspension or steering component degradation.",
        "probable_cause": "Worn control arm bushings, blown shocks/struts, or tie rod wear.",
        "severity": SeverityLevel.MEDIUM,
        "suggested_service": "Complete suspension and steering joint inspection",
        "estimated_cost": "$200–$600",
        "estimated_time": "2–4 hours",
    },
    CategoryChoices.BODY: {
        "summary": "Exterior body or panel damage.",
        "probable_cause": "Physical impact, weather wear, or seal degradation.",
        "severity": SeverityLevel.LOW,
        "suggested_service": "Bodywork repair and weatherstrip replacement",
        "estimated_cost": "$150–$500",
        "estimated_time": "2–6 hours",
    },
    CategoryChoices.GENERAL: {
        "summary": "General vehicle inspection recommended.",
        "probable_cause": "Multisystem wear or maintenance due.",
        "severity": SeverityLevel.MEDIUM,
        "suggested_service": "Comprehensive multi-point vehicle inspection",
        "estimated_cost": "$100–$250",
        "estimated_time": "1–2 hours",
    },
}


class GeminiService:

    @staticmethod
    def is_configured() -> bool:
        api_key = getattr(settings, "GEMINI_API_KEY", "")
        if not api_key or api_key == "your-gemini-api-key-here":
            return False
        genai.configure(api_key=api_key)
        return True

    @classmethod
    def analyze_media(cls, media_upload: MediaUpload) -> str:
        if not cls.is_configured():
            return ""

        try:
            with open(media_upload.file.path, "rb") as f:
                file_bytes = f.read()

            mime_map = {
                "image": "image/jpeg",
                "audio": "audio/mp3",
                "video": "video/mp4",
            }
            mime_type = mime_map.get(media_upload.media_type, "image/jpeg")

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": file_bytes,
                },
                (
                    "You are an automotive inspection expert. Analyze this uploaded "
                    f"{media_upload.media_type} of a vehicle and concisely summarize any visible "
                    "or audible mechanical defects, warning indicators, or wear patterns."
                ),
            ])
            return response.text or ""
        except Exception as exc:
            logger.warning("Gemini media analysis failed: %s", exc)
            return ""

    @classmethod
    def generate_diagnosis(cls, conversation: Conversation) -> Diagnosis:
        existing = Diagnosis.objects.filter(conversation=conversation).first()
        if existing:
            return existing

        if not cls.is_configured():
            return cls._create_rule_based_diagnosis(conversation)

        messages = conversation.messages.all()
        conversation_transcript = "\n".join(
            f"{msg.role.upper()}: {msg.text}" for msg in messages
        )

        media_summaries = []
        for media in conversation.media_uploads.all():
            if media.gemini_summary:
                media_summaries.append(f"[{media.media_type.upper()}] {media.gemini_summary}")

        media_context = (
            "\nMedia inspection notes:\n" + "\n".join(media_summaries)
            if media_summaries
            else ""
        )

        prompt = f"""
You are an expert master automotive diagnostic technician.
Analyze the following troubleshooting consultation and provide a structured JSON diagnosis.

Conversation:
{conversation_transcript}
{media_context}

Return ONLY valid JSON matching this schema:
{{
    "summary": "Concise 1-2 sentence overall summary of the diagnosed issue",
    "probable_cause": "The most likely underlying mechanical or electrical root cause",
    "severity": "low" | "medium" | "high" | "critical",
    "suggested_service": "Specific repair or service recommended",
    "estimated_cost": "Estimated price range, e.g. $150–$350",
    "estimated_time": "Estimated repair duration, e.g. 1–2 hours"
}}
"""
        try:
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
            )
            response = model.generate_content(prompt)
            data = json.loads(response.text)
            severity = data.get("severity", SeverityLevel.MEDIUM).lower()
            if severity not in SeverityLevel.values:
                severity = SeverityLevel.MEDIUM

            return Diagnosis.objects.create(
                conversation=conversation,
                summary=data.get("summary", "Automotive assessment completed."),
                probable_cause=data.get("probable_cause", "General component wear."),
                severity=severity,
                suggested_service=data.get("suggested_service", "Vehicle diagnostic check"),
                estimated_cost=data.get("estimated_cost", "$150–$300"),
                estimated_time=data.get("estimated_time", "1–2 hours"),
                is_ai_generated=True,
            )
        except Exception as exc:
            logger.warning("Gemini diagnosis failed: %s, falling back to rule engine", exc)
            return cls._create_rule_based_diagnosis(conversation)

    @classmethod
    def _create_rule_based_diagnosis(cls, conversation: Conversation) -> Diagnosis:
        category = conversation.category or CategoryChoices.GENERAL
        template = RULE_BASED_DIAGNOSES.get(category, RULE_BASED_DIAGNOSES[CategoryChoices.GENERAL])

        return Diagnosis.objects.create(
            conversation=conversation,
            summary=template["summary"],
            probable_cause=template["probable_cause"],
            severity=template["severity"],
            suggested_service=template["suggested_service"],
            estimated_cost=template["estimated_cost"],
            estimated_time=template["estimated_time"],
            is_ai_generated=False,
        )