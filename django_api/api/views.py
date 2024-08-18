#Alejandro Paredes La Torre
#Import necessary libraries
import pickle
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer
from django.shortcuts import render
#import joblib
import numpy as np
import pandas as pd

from datetime import datetime, date
#from asgiref.sync import async_to_sync
from api.components.nlp_huggingFace import DistillBERTClass
import asyncio
import logging
# Setting up logging
log_file = './mlapi_logs.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create your views here.
@api_view(['GET'])
def index_page(request):
    return_data = {
        "error" : "0",
        "message" : "Successfull Ok",
    } 
    logging.info("PRIMER GET") 
    print("PRIMER GET PRINT")
    return Response(return_data)


@api_view(["POST"])
#@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def prediction_nlp_huggingFace(request):
    try:
        comentario = request.data.get("comentario",None)
        #fields = [comentario,otroEj]
        if comentario is not None:
            comentario = str(comentario)      
            model = DistillBERTClass()
            comentario_limpieza = model.normalizar_remplazar(comentario)
            prediction, ouput, version = model.predict(comentario_limpieza)
            predictions = {
                'error' : '0',
                'message' : 'Successfull',
                'prediction' : prediction,
                'output' : ouput,
                'version' : version
            }
            return Response(predictions, status=200)
        else:
            predictions = {
                'error' : '1',
                'message': 'Invalid Parameters'                
            }
            return Response(predictions, status=406)
    except Exception as e:
        logging.error('Error predicting ./views/nlp_huggingFace: %s', e)
        predictions = {
            'error' : '2',
            "message": str(e)
        }
        return Response(predictions, status=502)
    


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def prediction_default_credit_risk(request):
    try:
        default_credit_risk_pred = default_credit_risk() 
        default_credit_risk_pred.default_credit_risk()
        logging.info(f'Response default_credit_risk sucessfully sended')
        return Response({'message': 'default_credit_risk successfully processed'},  status=200)
    except Exception as e:
        logging.error('Error predicting ./views/default_credit_risk: %s', e)
        predictions = {
            'error' : '2',
            "message": str(e)
        }
        return Response(predictions, status=502)