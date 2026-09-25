from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Conversation
from api.serializers import (
    ChatInputSerializer,
    ChatResponseSerializer,
    MessageSerializer,
)
from api.services.conversation_service import ConversationService


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