from django.urls import path
from api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'api' 

urlpatterns = [
    path('',views.index_page, name='index_page'),
    path('score_cobranzas/', views.prediction_score_cobranzas, name='score_cobranzas'),
    path('ganabert/', views.prediction_ganabert , name='prediction_ganabert')
]

