"""
DRF serializers for AutoMech AI.
Serializers handle validation, shape conversion, and provide the contract
between the API views and the internal models / service layer.
"""
from __future__ import annotations 
import re 
from typing import Any 
from django .conf import settings 
from rest_framework import serializers 
from api .models import (
Booking ,
Conversation ,
Diagnosis ,
MediaUpload ,
Message ,
)
EXTENSION_TO_MEDIA_TYPE :dict [str ,str ]={
"jpg":"image",
"jpeg":"image",
"png":"image",
"gif":"image",
"webp":"image",
"mp3":"audio",
"wav":"audio",
"ogg":"audio",
"webm":"audio",
"mp4":"video",
"webm":"video",
"mov":"video",
}
ALLOWED_EXTENSIONS :set [str ]=set (EXTENSION_TO_MEDIA_TYPE .keys ())
class ConversationSerializer (serializers .ModelSerializer ):
    """Read-only representation of a conversation."""
    class Meta :
        model =Conversation 
        fields =("id","created_at","updated_at","state","category","collected_data")
        read_only_fields =("id","created_at","updated_at")
class MessageSerializer (serializers .ModelSerializer ):
    """Representation of a single chat message."""
    class Meta :
        model =Message 
        fields =("id","role","text","created_at")
        read_only_fields =("id","role","created_at")
class ChatInputSerializer (serializers .Serializer ):
    """Validates incoming chat requests."""
    conversation_id =serializers .UUIDField (required =False ,allow_null =True )
    message =serializers .CharField (max_length =2000 )
class ChatResponseSerializer (serializers .Serializer ):
    """Shapes the chat API response."""
    conversation_id =serializers .UUIDField ()
    reply =serializers .CharField ()
    state =serializers .CharField ()
    category =serializers .CharField (allow_null =True )
    history =MessageSerializer (many =True )
class MediaUploadSerializer (serializers .ModelSerializer ):
    """Handles media upload with validation of type, size, and extension."""
    conversation_id =serializers .PrimaryKeyRelatedField (
    queryset =Conversation .objects .all (),
    source ="conversation",
    write_only =True ,
    )
    class Meta :
        model =MediaUpload 
        fields =(
        "id",
        "conversation_id",
        "file",
        "media_type",
        "original_filename",
        "size",
        "gemini_summary",
        "uploaded_at",
        )
        read_only_fields =(
        "id",
        "media_type",
        "original_filename",
        "size",
        "gemini_summary",
        "uploaded_at",
        )
    def validate_file (self ,value :Any )->Any :
        """Validate file extension and size."""
        name :str =value .name 
        ext =name .rsplit (".",1 )[-1 ].lower ()if "."in name else ""
        if ext not in ALLOWED_EXTENSIONS :
            raise serializers .ValidationError (
            f"Unsupported file type '.{ext }'. "
            f"Allowed: {', '.join (sorted (ALLOWED_EXTENSIONS ))}"
            )
        max_bytes =settings .MAX_UPLOAD_SIZE_MB *1024 *1024 
        if value .size >max_bytes :
            raise serializers .ValidationError (
            f"File too large ({value .size /1024 /1024 :.1f} MB). "
            f"Maximum allowed: {settings .MAX_UPLOAD_SIZE_MB } MB."
            )
        return value 
    def create (self ,validated_data :dict [str ,Any ])->MediaUpload :
        """Set derived fields from the uploaded file."""
        uploaded_file =validated_data ["file"]
        name :str =uploaded_file .name 
        ext =name .rsplit (".",1 )[-1 ].lower ()
        validated_data ["original_filename"]=name 
        validated_data ["size"]=uploaded_file .size 
        validated_data ["media_type"]=EXTENSION_TO_MEDIA_TYPE [ext ]
        return super ().create (validated_data )
class DiagnosisSerializer (serializers .ModelSerializer ):
    """Read-only serializer for diagnosis results."""
    class Meta :
        model =Diagnosis 
        fields =(
        "id",
        "conversation_id",
        "summary",
        "probable_cause",
        "severity",
        "suggested_service",
        "estimated_cost",
        "estimated_time",
        "is_ai_generated",
        "created_at",
        )
        read_only_fields =fields 
class BookingInputSerializer (serializers .Serializer ):
    """Validates mechanic booking requests."""
    diagnosis_id =serializers .IntegerField ()
    customer_name =serializers .CharField (max_length =100 )
    phone =serializers .CharField (max_length =20 )
    vehicle =serializers .CharField (max_length =200 )
    preferred_slot =serializers .CharField (max_length =100 )
    def validate_phone (self ,value :str )->str :
        """Phone must contain only digits, spaces, hyphens, and plus."""
        cleaned =value .strip ()
        if not re .match (r"^[\d\s\-\+]+$",cleaned ):
            raise serializers .ValidationError (
            "Phone number may only contain digits, spaces, hyphens, and '+'."
            )
        digits =re .sub (r"\D","",cleaned )
        if not (7 <=len (digits )<=15 ):
            raise serializers .ValidationError (
            "Phone number must have between 7 and 15 digits."
            )
        return cleaned 
class BookingSerializer (serializers .ModelSerializer ):
    """Full booking representation with nested diagnosis."""
    diagnosis =DiagnosisSerializer (read_only =True )
    class Meta :
        model =Booking 
        fields =(
        "id",
        "diagnosis",
        "customer_name",
        "phone",
        "vehicle",
        "preferred_slot",
        "status",
        "created_at",
        )
        read_only_fields =("id","status","created_at")
