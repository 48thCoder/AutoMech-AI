from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Booking, Conversation, ConversationState, Diagnosis
from api.serializers import (
    BookingInputSerializer,
    BookingSerializer,
    ChatInputSerializer,
    ChatResponseSerializer,
    DiagnosisSerializer,
    MediaUploadSerializer,
    MessageSerializer,
)
from api.services.conversation_service import ConversationService
from api.services.gemini_service import GeminiService


class ChatView(APIView):

    def post(self, request: Request) -> Response:
        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data.get("conversation_id")
        user_message: str = serializer.validated_data["message"]

        conversation = ConversationService.get_or_create_conversation(conversation_id)
        reply, updated_conversation = ConversationService.process_user_message(
            conversation=conversation,
            user_text=user_message,
        )

        history = updated_conversation.messages.all()

        response_data = {
            "conversation_id": updated_conversation.id,
            "reply": reply,
            "state": updated_conversation.state,
            "category": updated_conversation.category,
            "history": MessageSerializer(history, many=True).data,
        }

        response_serializer = ChatResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MediaUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: Request) -> Response:
        serializer = MediaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media_upload = serializer.save()

        summary = GeminiService.analyze_media(media_upload)
        if summary:
            media_upload.gemini_summary = summary
            media_upload.save(update_fields=["gemini_summary"])

        return Response(
            MediaUploadSerializer(media_upload).data,
            status=status.HTTP_201_CREATED,
        )


class DiagnosisView(APIView):

    def post(self, request: Request) -> Response:
        conversation_id = request.data.get("conversation_id")
        if not conversation_id:
            return Response(
                {"detail": "conversation_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = get_object_or_404(Conversation, id=conversation_id)
        diagnosis = GeminiService.generate_diagnosis(conversation)

        conversation.state = ConversationState.DIAGNOSED
        conversation.save(update_fields=["state"])

        return Response(
            DiagnosisSerializer(diagnosis).data,
            status=status.HTTP_200_OK,
        )


class BookingCreateView(APIView):

    def post(self, request: Request) -> Response:
        serializer = BookingInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        diagnosis_id = serializer.validated_data["diagnosis_id"]
        diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id)

        if hasattr(diagnosis, "booking"):
            return Response(
                {"detail": "A booking already exists for this diagnosis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking = Booking.objects.create(
            diagnosis=diagnosis,
            customer_name=serializer.validated_data["customer_name"],
            phone=serializer.validated_data["phone"],
            vehicle=serializer.validated_data["vehicle"],
            preferred_slot=serializer.validated_data["preferred_slot"],
        )

        conversation = diagnosis.conversation
        conversation.state = ConversationState.BOOKED
        conversation.save(update_fields=["state"])

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(APIView):

    def get(self, request: Request, pk: str) -> Response:
        booking = get_object_or_404(Booking, id=pk)
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK,
        )