"""
Django settings for AutoMech AI project.
Environment-based configuration using python-dotenv.
"""
from __future__ import annotations 
import os 
from pathlib import Path 
from dotenv import load_dotenv 
BASE_DIR =Path (__file__ ).resolve ().parent .parent 
load_dotenv (BASE_DIR /".env")
SECRET_KEY :str =os .getenv ("SECRET_KEY","insecure-dev-key-change-me")
DEBUG :bool =os .getenv ("DEBUG","True").lower ()in ("true","1","yes")
ALLOWED_HOSTS :list [str ]=[
h .strip ()
for h in os .getenv ("ALLOWED_HOSTS","localhost,127.0.0.1").split (",")
if h .strip ()
]
INSTALLED_APPS :list [str ]=[
"django.contrib.admin",
"django.contrib.auth",
"django.contrib.contenttypes",
"django.contrib.sessions",
"django.contrib.messages",
"django.contrib.staticfiles",
"rest_framework",
"corsheaders",
"drf_spectacular",
"api",
]
MIDDLEWARE :list [str ]=[
"corsheaders.middleware.CorsMiddleware",
"django.middleware.security.SecurityMiddleware",
"django.contrib.sessions.middleware.SessionMiddleware",
"django.middleware.common.CommonMiddleware",
"django.middleware.csrf.CsrfViewMiddleware",
"django.contrib.auth.middleware.AuthenticationMiddleware",
"django.contrib.messages.middleware.MessageMiddleware",
"django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF ="config.urls"
TEMPLATES =[
{
"BACKEND":"django.template.backends.django.DjangoTemplates",
"DIRS":[],
"APP_DIRS":True ,
"OPTIONS":{
"context_processors":[
"django.template.context_processors.debug",
"django.template.context_processors.request",
"django.contrib.auth.context_processors.auth",
"django.contrib.messages.context_processors.messages",
],
},
},
]
WSGI_APPLICATION ="config.wsgi.application"
DATABASES ={
"default":{
"ENGINE":"django.db.backends.sqlite3",
"NAME":BASE_DIR /"db.sqlite3",
}
}
AUTH_PASSWORD_VALIDATORS =[
{"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},
{"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},
{"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE ="en-us"
TIME_ZONE ="UTC"
USE_I18N =True 
USE_TZ =True 
STATIC_URL ="static/"
STATIC_ROOT =BASE_DIR /"staticfiles"
MEDIA_URL ="media/"
MEDIA_ROOT =BASE_DIR /os .getenv ("MEDIA_ROOT","media")
DEFAULT_AUTO_FIELD ="django.db.models.BigAutoField"
CORS_ALLOWED_ORIGINS :list [str ]=[
o .strip ()
for o in os .getenv ("CORS_ALLOWED_ORIGINS","http://localhost:3000").split (",")
if o .strip ()
]
REST_FRAMEWORK ={
"DEFAULT_RENDERER_CLASSES":[
"rest_framework.renderers.JSONRenderer",
],
"DEFAULT_EXCEPTION_HANDLER":"api.exceptions.global_exception_handler",
"DEFAULT_SCHEMA_CLASS":"drf_spectacular.openapi.AutoSchema",
}
SPECTACULAR_SETTINGS ={
"TITLE":"AutoMech AI API",
"DESCRIPTION":(
"API for the AI Car Mechanic Chatbot. "
"Chat with a virtual senior automobile technician to troubleshoot "
"and diagnose car problems, then optionally book a mechanic."
),
"VERSION":"1.0.0",
"SERVE_INCLUDE_SCHEMA":False ,
}
GEMINI_API_KEY :str =os .getenv ("GEMINI_API_KEY","")
MAX_UPLOAD_SIZE_MB :int =int (os .getenv ("MAX_UPLOAD_SIZE_MB","25"))
