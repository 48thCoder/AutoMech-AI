from __future__ import annotations

import re
from typing import Any

from api.models import (
    CategoryChoices,
    Conversation,
    ConversationState,
    Message,
    MessageRole,
)

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    CategoryChoices.ENGINE: [
        "engine", "motor", "smoke", "overheat", "overheating", "oil", "oil leak",
        "stalling", "misfire", "check engine", "cel", "radiator", "coolant", "exhaust"
    ],
    CategoryChoices.BRAKES: [
        "brake", "brakes", "braking", "squeak", "squeal", "grinding", "pedal",
        "rotor", "rotors", "pad", "pads", "abs", "stopping", "soft pedal"
    ],
    CategoryChoices.ELECTRICAL: [
        "battery", "alternator", "starter", "starting", "lights", "headlight",
        "turn signal", "fuse", "radio", "screen", "power window", "dead battery"
    ],
    CategoryChoices.TYRES: [
        "tire", "tires", "tyre", "tyres", "flat", "puncture", "pressure", "alignment",
        "tpms", "tread", "vibration", "wobble", "blowout"
    ],
    CategoryChoices.AC: [
        "ac", "a/c", "air condition", "air conditioning", "heater", "heating",
        "blows warm", "vent", "vents", "smell", "compressor", "defroster"
    ],
    CategoryChoices.TRANSMISSION: [
        "transmission", "gear", "gears", "shifting", "slipping", "clutch", "reverse",
        "automatic", "manual", "trans fluid"
    ],
    CategoryChoices.SUSPENSION: [
        "suspension", "shock", "shocks", "strut", "struts", "bumpy", "bouncing",
        "knocking", "clunk", "steering", "pulling", "control arm"
    ],
    CategoryChoices.BODY: [
        "dent", "scratch", "bumper", "door", "window", "windshield", "crack", "paint",
        "rust", "fender", "hood", "trunk"
    ],
}

CATEGORY_FOLLOWUPS: dict[str, list[str]] = {
    CategoryChoices.ENGINE: [
        "Does the Check Engine Light illuminate, flash, or stay solid on your dashboard?",
        "Do you notice any smoke from the exhaust or under the hood, and what color is it (white, blue, black)?",
        "Does the issue occur only when the engine is cold, at idle, or during acceleration?",
    ],
    CategoryChoices.BRAKES: [
        "Do you hear a high-pitched squeal or a harsh grinding metal sound when applying the brakes?",
        "Does the brake pedal feel soft/spongy, or does the vehicle pull to one side when stopping?",
        "Do you feel any pulsation or shaking through the pedal or steering wheel when braking?",
    ],
    CategoryChoices.ELECTRICAL: [
        "Does the engine crank slowly, make a rapid clicking noise, or is there complete silence when you turn the key/press start?",
        "Do your headlights or dashboard lights flicker or dim while driving or idling?",
        "Have you needed to jump-start the car recently, or has the battery warning light stayed on?",
    ],
    CategoryChoices.TYRES: [
        "Is there visible tire damage, uneven tread wear, or is a specific tire losing pressure?",
        "Do you feel vibration in the steering wheel or seat at specific speeds (e.g., highway speeds)?",
        "Has the TPMS (Tire Pressure Monitoring System) warning light appeared on your dashboard?",
    ],
    CategoryChoices.AC: [
        "Is the air coming out of the vents completely ambient/warm, or only mildly cool?",
        "Does the blower fan operate at all speeds, and do you hear any unusual rattling when AC is activated?",
        "Do you notice any dampness, chemical odor, or musty smell when the AC is turned on?",
    ],
    CategoryChoices.TRANSMISSION: [
        "Is there a delay or harsh jerk when shifting between Park, Reverse, and Drive?",
        "Does the engine rev high without the vehicle accelerating properly (slipping gears)?",
        "Have you noticed any reddish fluid leaking beneath the vehicle?",
    ],
    CategoryChoices.SUSPENSION: [
        "Do you hear clunking, knocking, or squeaking noises when going over bumps or turning?",
        "Does the car pull to the left or right when driving straight on a level road?",
        "Does the car continue to bounce excessively after hitting dips or speed bumps?",
    ],
    CategoryChoices.BODY: [
        "Is there visible structural damage, panel misalignment, or deep paint scratching/rust?",
        "Are any doors, windows, trunk, or the hood unable to latch or seal properly?",
        "Does water leak into the cabin during rain or car washes?",
    ],
    CategoryChoices.GENERAL: [
        "Can you describe any strange sounds, smells, or dashboard warning lights you have noticed?",
        "When did you first notice this problem, and has it gotten progressively worse?",
        "What is the approximate year, make, model, and mileage of your vehicle?",
    ],
}


class ConversationService:

    @staticmethod
    def get_or_create_conversation(conversation_id: str | None = None) -> Conversation:
        if conversation_id:
            try:
                return Conversation.objects.get(id=conversation_id)
            except (Conversation.DoesNotExist, ValueError):
                pass
        return Conversation.objects.create(state=ConversationState.GATHERING)

    @classmethod
    def detect_category(cls, user_text: str) -> str:
        text = user_text.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", text):
                    return category
        return CategoryChoices.GENERAL

    @classmethod
    def process_user_message(cls, conversation: Conversation, user_text: str) -> tuple[str, Conversation]:
        Message.objects.create(
            conversation=conversation,
            role=MessageRole.USER,
            text=user_text,
        )

        data: dict[str, Any] = conversation.collected_data or {}
        answers = data.setdefault("answers", [])
        answers.append(user_text)

        if not conversation.category or conversation.category == CategoryChoices.GENERAL:
            detected = cls.detect_category(user_text)
            if detected != CategoryChoices.GENERAL or not conversation.category:
                conversation.category = detected

        category = conversation.category or CategoryChoices.GENERAL
        questions = CATEGORY_FOLLOWUPS.get(category, CATEGORY_FOLLOWUPS[CategoryChoices.GENERAL])
        current_step = data.get("current_step", 0)

        if conversation.state == ConversationState.GATHERING:
            if current_step < len(questions):
                reply = questions[current_step]
                data["current_step"] = current_step + 1
                if data["current_step"] >= len(questions):
                    conversation.state = ConversationState.READY_FOR_DIAGNOSIS
            else:
                conversation.state = ConversationState.READY_FOR_DIAGNOSIS
                reply = (
                    "Thank you for providing those details. I have gathered enough information to evaluate "
                    "your vehicle's condition. You can now request a comprehensive diagnostic report, "
                    "or upload an image, audio clip, or video to assist the diagnosis."
                )
        elif conversation.state == ConversationState.READY_FOR_DIAGNOSIS:
            reply = (
                "I have all preliminary details recorded. You can proceed with requesting your diagnosis, "
                "or upload photos or sound recordings for deeper analysis."
            )
        elif conversation.state == ConversationState.DIAGNOSED:
            reply = (
                "Your diagnostic evaluation has already been prepared. You can review the recommendations "
                "or proceed to book a qualified mechanic for service."
            )
        elif conversation.state == ConversationState.BOOKING_OFFERED:
            reply = (
                "We are ready to schedule your service appointment. Please submit your booking details "
                "or preferred date and time."
            )
        elif conversation.state == ConversationState.BOOKED:
            reply = (
                "Your mechanic appointment is already booked. If you need any further assistance or "
                "wish to troubleshoot another issue, feel free to start a new consultation."
            )
        else:
            reply = "How can I assist you with your vehicle today?"

        conversation.collected_data = data
        conversation.save()

        Message.objects.create(
            conversation=conversation,
            role=MessageRole.BOT,
            text=reply,
        )

        return reply, conversation