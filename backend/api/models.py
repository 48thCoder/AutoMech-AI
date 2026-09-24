"""
Database models for the AutoMech AI chatbot.
Models:
    - Conversation: Tracks a chat session and its state machine progression.
    - Message: Individual messages within a conversation.
    - MediaUpload: Files (image/audio/video) uploaded during a conversation.
    - Diagnosis: AI-generated or rule-based diagnosis for a conversation.
    - Booking: Mechanic appointment booked after a diagnosis.
"""
from __future__ import annotations 
import uuid 
from django .db import models 
class ConversationState (models .TextChoices ):
    """State machine states for conversation flow."""
    GATHERING ="gathering","Gathering Info"
    READY_FOR_DIAGNOSIS ="ready_for_diagnosis","Ready for Diagnosis"
    DIAGNOSED ="diagnosed","Diagnosed"
    BOOKING_OFFERED ="booking_offered","Booking Offered"
    BOOKED ="booked","Booked"
class CategoryChoices (models .TextChoices ):
    """Car problem categories detected from user input."""
    ENGINE ="engine","Engine"
    BRAKES ="brakes","Brakes"
    ELECTRICAL ="electrical","Electrical"
    TYRES ="tyres","Tyres"
    AC ="ac","AC / Climate"
    TRANSMISSION ="transmission","Transmission"
    SUSPENSION ="suspension","Suspension"
    BODY ="body","Body / Exterior"
    GENERAL ="general","General"
class MessageRole (models .TextChoices ):
    """Who sent the message."""
    USER ="user","User"
    BOT ="bot","Bot"
class MediaType (models .TextChoices ):
    """Type of uploaded media."""
    IMAGE ="image","Image"
    AUDIO ="audio","Audio"
    VIDEO ="video","Video"
class SeverityLevel (models .TextChoices ):
    """How severe the diagnosed problem is."""
    LOW ="low","Low"
    MEDIUM ="medium","Medium"
    HIGH ="high","High"
    CRITICAL ="critical","Critical"
class BookingStatus (models .TextChoices ):
    """Status of a mechanic booking."""
    PENDING ="pending","Pending"
    CONFIRMED ="confirmed","Confirmed"
    CANCELLED ="cancelled","Cancelled"
class Conversation (models .Model ):
    """
    A single troubleshooting conversation with a car owner.
    Tracks the state machine (GATHERING → BOOKED), detected category,
    and all collected answers in a JSON field.
    """
    id =models .UUIDField (
    primary_key =True ,
    default =uuid .uuid4 ,
    editable =False ,
    )
    created_at =models .DateTimeField (auto_now_add =True )
    updated_at =models .DateTimeField (auto_now =True )
    state =models .CharField (
    max_length =30 ,
    choices =ConversationState .choices ,
    default =ConversationState .GATHERING ,
    )
    category =models .CharField (
    max_length =30 ,
    choices =CategoryChoices .choices ,
    null =True ,
    blank =True ,
    )
    collected_data =models .JSONField (default =dict ,blank =True )
    class Meta :
        ordering =["-created_at"]
    def __str__ (self )->str :
        return f"Conversation {self .id } [{self .state }]"
class Message (models .Model ):
    """An individual message in a conversation (user or bot)."""
    id =models .BigAutoField (primary_key =True )
    conversation =models .ForeignKey (
    Conversation ,
    on_delete =models .CASCADE ,
    related_name ="messages",
    )
    role =models .CharField (
    max_length =10 ,
    choices =MessageRole .choices ,
    )
    text =models .TextField ()
    created_at =models .DateTimeField (auto_now_add =True )
    class Meta :
        ordering =["created_at"]
    def __str__ (self )->str :
        return f"[{self .role }] {self .text [:60 ]}"
class MediaUpload (models .Model ):
    """A media file (image/audio/video) uploaded during a conversation."""
    id =models .BigAutoField (primary_key =True )
    conversation =models .ForeignKey (
    Conversation ,
    on_delete =models .CASCADE ,
    related_name ="media_uploads",
    )
    file =models .FileField (upload_to ="uploads/%Y/%m/%d/")
    media_type =models .CharField (
    max_length =10 ,
    choices =MediaType .choices ,
    )
    original_filename =models .CharField (max_length =255 )
    size =models .PositiveIntegerField (help_text ="File size in bytes")
    gemini_summary =models .TextField (blank =True ,default ="")
    uploaded_at =models .DateTimeField (auto_now_add =True )
    def __str__ (self )->str :
        return f"{self .media_type }: {self .original_filename }"
class Diagnosis (models .Model ):
    """
    Diagnosis result for a conversation.
    May be AI-generated (Gemini) or rule-based fallback.
    """
    id =models .BigAutoField (primary_key =True )
    conversation =models .OneToOneField (
    Conversation ,
    on_delete =models .CASCADE ,
    related_name ="diagnosis",
    )
    summary =models .TextField ()
    probable_cause =models .TextField ()
    severity =models .CharField (
    max_length =20 ,
    choices =SeverityLevel .choices ,
    )
    suggested_service =models .CharField (max_length =200 )
    estimated_cost =models .CharField (
    max_length =100 ,
    help_text ="e.g. '$200–$400'",
    )
    estimated_time =models .CharField (
    max_length =100 ,
    help_text ="e.g. '2–3 hours'",
    )
    is_ai_generated =models .BooleanField (
    default =False ,
    help_text ="True if Gemini was used, False if rule-based fallback",
    )
    created_at =models .DateTimeField (auto_now_add =True )
    class Meta :
        verbose_name_plural ="diagnoses"
    def __str__ (self )->str :
        return f"Diagnosis for {self .conversation_id }: {self .summary [:60 ]}"
class Booking (models .Model ):
    """Mechanic appointment booking linked to a diagnosis."""
    id =models .UUIDField (
    primary_key =True ,
    default =uuid .uuid4 ,
    editable =False ,
    )
    diagnosis =models .OneToOneField (
    Diagnosis ,
    on_delete =models .CASCADE ,
    related_name ="booking",
    )
    customer_name =models .CharField (max_length =100 )
    phone =models .CharField (max_length =20 )
    vehicle =models .CharField (
    max_length =200 ,
    help_text ="e.g. '2020 Toyota Camry'",
    )
    preferred_slot =models .CharField (
    max_length =100 ,
    help_text ="e.g. 'Tomorrow 10 AM'",
    )
    status =models .CharField (
    max_length =20 ,
    choices =BookingStatus .choices ,
    default =BookingStatus .PENDING ,
    )
    created_at =models .DateTimeField (auto_now_add =True )
    def __str__ (self )->str :
        return f"Booking {self .id } – {self .customer_name } ({self .status })"
