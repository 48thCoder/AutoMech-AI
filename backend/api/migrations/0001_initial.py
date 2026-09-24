from django .db import migrations ,models 
import django .db .models .deletion 
import uuid 
class Migration (migrations .Migration ):
    initial =True 
    dependencies =[
    ]
    operations =[
    migrations .CreateModel (
    name ='Conversation',
    fields =[
    ('id',models .UUIDField (default =uuid .uuid4 ,editable =False ,primary_key =True ,serialize =False )),
    ('created_at',models .DateTimeField (auto_now_add =True )),
    ('updated_at',models .DateTimeField (auto_now =True )),
    ('state',models .CharField (choices =[('gathering','Gathering Info'),('ready_for_diagnosis','Ready for Diagnosis'),('diagnosed','Diagnosed'),('booking_offered','Booking Offered'),('booked','Booked')],default ='gathering',max_length =30 )),
    ('category',models .CharField (blank =True ,choices =[('engine','Engine'),('brakes','Brakes'),('electrical','Electrical'),('tyres','Tyres'),('ac','AC / Climate'),('transmission','Transmission'),('suspension','Suspension'),('body','Body / Exterior'),('general','General')],max_length =30 ,null =True )),
    ('collected_data',models .JSONField (blank =True ,default =dict )),
    ],
    options ={
    'ordering':['-created_at'],
    },
    ),
    migrations .CreateModel (
    name ='Message',
    fields =[
    ('id',models .BigAutoField (primary_key =True ,serialize =False )),
    ('role',models .CharField (choices =[('user','User'),('bot','Bot')],max_length =10 )),
    ('text',models .TextField ()),
    ('created_at',models .DateTimeField (auto_now_add =True )),
    ('conversation',models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ='messages',to ='api.conversation')),
    ],
    options ={
    'ordering':['created_at'],
    },
    ),
    migrations .CreateModel (
    name ='MediaUpload',
    fields =[
    ('id',models .BigAutoField (primary_key =True ,serialize =False )),
    ('file',models .FileField (upload_to ='uploads/%Y/%m/%d/')),
    ('media_type',models .CharField (choices =[('image','Image'),('audio','Audio'),('video','Video')],max_length =10 )),
    ('original_filename',models .CharField (max_length =255 )),
    ('size',models .PositiveIntegerField (help_text ='File size in bytes')),
    ('gemini_summary',models .TextField (blank =True ,default ='')),
    ('uploaded_at',models .DateTimeField (auto_now_add =True )),
    ('conversation',models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ='media_uploads',to ='api.conversation')),
    ],
    ),
    migrations .CreateModel (
    name ='Diagnosis',
    fields =[
    ('id',models .BigAutoField (primary_key =True ,serialize =False )),
    ('summary',models .TextField ()),
    ('probable_cause',models .TextField ()),
    ('severity',models .CharField (choices =[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')],max_length =20 )),
    ('suggested_service',models .CharField (max_length =200 )),
    ('estimated_cost',models .CharField (help_text ="e.g. '$200–$400'",max_length =100 )),
    ('estimated_time',models .CharField (help_text ="e.g. '2–3 hours'",max_length =100 )),
    ('is_ai_generated',models .BooleanField (default =False ,help_text ='True if Gemini was used, False if rule-based fallback')),
    ('created_at',models .DateTimeField (auto_now_add =True )),
    ('conversation',models .OneToOneField (on_delete =django .db .models .deletion .CASCADE ,related_name ='diagnosis',to ='api.conversation')),
    ],
    options ={
    'verbose_name_plural':'diagnoses',
    },
    ),
    migrations .CreateModel (
    name ='Booking',
    fields =[
    ('id',models .UUIDField (default =uuid .uuid4 ,editable =False ,primary_key =True ,serialize =False )),
    ('customer_name',models .CharField (max_length =100 )),
    ('phone',models .CharField (max_length =20 )),
    ('vehicle',models .CharField (help_text ="e.g. '2020 Toyota Camry'",max_length =200 )),
    ('preferred_slot',models .CharField (help_text ="e.g. 'Tomorrow 10 AM'",max_length =100 )),
    ('status',models .CharField (choices =[('pending','Pending'),('confirmed','Confirmed'),('cancelled','Cancelled')],default ='pending',max_length =20 )),
    ('created_at',models .DateTimeField (auto_now_add =True )),
    ('diagnosis',models .OneToOneField (on_delete =django .db .models .deletion .CASCADE ,related_name ='booking',to ='api.diagnosis')),
    ],
    ),
    ]
