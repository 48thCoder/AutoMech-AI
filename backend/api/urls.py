from __future__ import annotations

from django.urls import path

from api import views

urlpatterns: list = [
    path("chat/", views.ChatView.as_view(), name="chat"),
    path("upload/", views.MediaUploadView.as_view(), name="upload"),
    path("diagnosis/", views.DiagnosisView.as_view(), name="diagnosis"),
    path("booking/", views.BookingCreateView.as_view(), name="booking-create"),
    path("booking/<uuid:pk>/", views.BookingDetailView.as_view(), name="booking-detail"),
]