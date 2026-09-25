from __future__ import annotations

from django.urls import path

from api import views

urlpatterns: list = [
    path("chat/", views.ChatView.as_view(), name="chat"),
]