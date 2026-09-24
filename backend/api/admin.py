"""Admin registrations for AutoMech AI models."""
from __future__ import annotations 
from django .contrib import admin 
from api .models import Booking ,Conversation ,Diagnosis ,MediaUpload ,Message 
@admin .register (Conversation )
class ConversationAdmin (admin .ModelAdmin ):
    list_display =("id","state","category","created_at","updated_at")
    list_filter =("state","category")
    search_fields =("id",)
    readonly_fields =("id","created_at","updated_at")
@admin .register (Message )
class MessageAdmin (admin .ModelAdmin ):
    list_display =("id","conversation_id","role","short_text","created_at")
    list_filter =("role",)
    search_fields =("text",)
    readonly_fields =("created_at",)
    @admin .display (description ="Text")
    def short_text (self ,obj :Message )->str :
        return obj .text [:80 ]+("…"if len (obj .text )>80 else "")
@admin .register (MediaUpload )
class MediaUploadAdmin (admin .ModelAdmin ):
    list_display =(
    "id",
    "conversation_id",
    "media_type",
    "original_filename",
    "size",
    "uploaded_at",
    )
    list_filter =("media_type",)
    search_fields =("original_filename",)
    readonly_fields =("uploaded_at",)
@admin .register (Diagnosis )
class DiagnosisAdmin (admin .ModelAdmin ):
    list_display =(
    "id",
    "conversation_id",
    "severity",
    "suggested_service",
    "is_ai_generated",
    "created_at",
    )
    list_filter =("severity","is_ai_generated")
    readonly_fields =("created_at",)
@admin .register (Booking )
class BookingAdmin (admin .ModelAdmin ):
    list_display =(
    "id",
    "customer_name",
    "phone",
    "vehicle",
    "preferred_slot",
    "status",
    "created_at",
    )
    list_filter =("status",)
    search_fields =("customer_name","phone","vehicle")
    readonly_fields =("id","created_at")
