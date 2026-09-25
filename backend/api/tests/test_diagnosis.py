from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from api.models import CategoryChoices, Conversation, ConversationState, Diagnosis


class DiagnosisAndMediaAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_media_upload_endpoint(self):
        conv = Conversation.objects.create()
        fake_image = SimpleUploadedFile(
            "dashboard_light.jpg",
            b"fake-image-bytes",
            content_type="image/jpeg",
        )

        response = self.client.post(
            "/api/upload/",
            {"conversation_id": str(conv.id), "file": fake_image},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["original_filename"], "dashboard_light.jpg")
        self.assertEqual(data["media_type"], "image")

    def test_diagnosis_generation_fallback(self):
        conv = Conversation.objects.create(
            state=ConversationState.READY_FOR_DIAGNOSIS,
            category=CategoryChoices.BRAKES,
        )

        response = self.client.post(
            "/api/diagnosis/",
            {"conversation_id": str(conv.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("probable_cause", data)
        self.assertIn("suggested_service", data)
        self.assertEqual(data["severity"], "critical")

        conv.refresh_from_db()
        self.assertEqual(conv.state, ConversationState.DIAGNOSED)
        self.assertTrue(Diagnosis.objects.filter(conversation=conv).exists())