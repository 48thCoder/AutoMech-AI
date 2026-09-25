from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from api.models import CategoryChoices, Conversation, ConversationState


class ChatAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_start_new_conversation(self):
        response = self.client.post("/api/chat/", {"message": "My car engine is overheating and making noise"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("conversation_id", data)
        self.assertEqual(data["category"], CategoryChoices.ENGINE)
        self.assertEqual(data["state"], ConversationState.GATHERING)
        self.assertEqual(len(data["history"]), 2)

    def test_continue_conversation_to_ready(self):
        conv = Conversation.objects.create(state=ConversationState.GATHERING, category=CategoryChoices.BRAKES)
        
        response = self.client.post("/api/chat/", {"conversation_id": str(conv.id), "message": "High pitched squeal"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post("/api/chat/", {"conversation_id": str(conv.id), "message": "Pedal feels spongy"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post("/api/chat/", {"conversation_id": str(conv.id), "message": "Shaking when braking"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        conv.refresh_from_db()
        self.assertEqual(conv.state, ConversationState.READY_FOR_DIAGNOSIS)