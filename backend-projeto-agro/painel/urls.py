from django.urls import path
from .views import DashboardAdminAPIView

urlpatterns = [
    path('dashboard/', DashboardAdminAPIView.as_view(), name='dashboard-admin'),
] 