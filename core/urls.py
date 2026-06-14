from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', views.register),
    path('api/auth/login/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/analyze/', views.analyze_post),
    path('api/history/', views.fetch_history),
    path('api/report/', views.report_scam),
]