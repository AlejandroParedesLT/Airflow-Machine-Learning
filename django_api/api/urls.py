from django.urls import path
from api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'api' 

urlpatterns = [
    path('',views.index_page, name='index_page'),
    path('default_credit_risk/', views.default_credit_risk, name='default_credit_risk'),
    path('nlp_huggingFace/', views.nlp_huggingFace , name='nlp_huggingFace')
]

