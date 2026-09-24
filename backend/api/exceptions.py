"""
Global DRF exception handler for consistent JSON error responses.
Every error returned by the API follows this shape:
{
    "success": false,
    "error": {
        "code": <HTTP status code>,
        "message": "<human-readable summary>",
        "details": { ... } | null
    }
}
"""
from __future__ import annotations 
import logging 
from typing import Any 
from rest_framework import status 
from rest_framework .response import Response 
from rest_framework .views import exception_handler 
logger =logging .getLogger (__name__ )
def global_exception_handler (
exc :Exception ,context :dict [str ,Any ]
)->Response :
    """Return consistent JSON errors for all DRF exceptions."""
    response =exception_handler (exc ,context )
    if response is not None :
        error_data ={
        "success":False ,
        "error":{
        "code":response .status_code ,
        "message":_extract_message (response .data ),
        "details":response .data if isinstance (response .data ,dict )else None ,
        },
        }
        response .data =error_data 
        return response 
    logger .exception ("Unhandled exception: %s",exc )
    return Response (
    {
    "success":False ,
    "error":{
    "code":500 ,
    "message":"An unexpected error occurred. Please try again later.",
    "details":None ,
    },
    },
    status =status .HTTP_500_INTERNAL_SERVER_ERROR ,
    )
def _extract_message (data :Any )->str :
    """Pull a human-readable message from DRF's default error data."""
    if isinstance (data ,dict ):
        if "detail"in data :
            return str (data ["detail"])
        first_key =next (iter (data ),None )
        if first_key :
            val =data [first_key ]
            if isinstance (val ,list ):
                return f"{first_key }: {val [0 ]}"
            return f"{first_key }: {val }"
    if isinstance (data ,list ):
        return str (data [0 ])
    return str (data )
