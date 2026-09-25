from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from api.models import (
    Booking,
    BookingStatus,
    Conversation,
    ConversationState,
    Diagnosis,
    SeverityLevel,
)


class BookingAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.conversation = Conversation.objects.create(state=ConversationState.DIAGNOSED)
        self.diagnosis = Diagnosis.objects.create(
            conversation=self.conversation,
            summary="Brake pad wear detected",
            probable_cause="Worn front pads",
            severity=SeverityLevel.HIGH,
            suggested_service="Brake pad replacement",
            estimated_cost="$200–$300",
            estimated_time="1–2 hours",
        )

    def test_create_booking_success(self):
        payload = {
            "diagnosis_id": self.diagnosis.id,
            "customer_name": "John Doe",
            "phone": "+1-555-0199",
            "vehicle": "2021 Honda Civic",
            "preferred_slot": "Tomorrow at 10:00 AM",
        }
        response = self.client.post("/api/booking/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["customer_name"], "John Doe")
        self.assertEqual(data["status"], BookingStatus.PENDING)
        self.assertEqual(data["diagnosis"]["id"], self.diagnosis.id)

        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.state, ConversationState.BOOKED)

    def test_create_duplicate_booking_fails(self):
        Booking.objects.create(
            diagnosis=self.diagnosis,
            customer_name="Existing Customer",
            phone="+1-555-0100",
            vehicle="2020 Toyota Camry",
            preferred_slot="Friday 2 PM",
        )
        payload = {
            "diagnosis_id": self.diagnosis.id,
            "customer_name": "John Doe",
            "phone": "+1-555-0199",
            "vehicle": "2021 Honda Civic",
            "preferred_slot": "Tomorrow at 10:00 AM",
        }
        response = self.client.post("/api/booking/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_booking_detail(self):
        booking = Booking.objects.create(
            diagnosis=self.diagnosis,
            customer_name="Alice Smith",
            phone="+1-555-0144",
            vehicle="2019 Ford F-150",
            preferred_slot="Monday 9 AM",
        )
        response = self.client.get(f"/api/booking/{booking.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], str(booking.id))
        self.assertEqual(data["customer_name"], "Alice Smith")