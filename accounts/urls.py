from django.urls import path
from . import views
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LogInView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllDevicesView.as_view(), name='logout_all'),
    path('devices/', UserDevicesListView.as_view(), name='devices_list'),   
    path('add-coins/', AddCoinsRewardView.as_view(), name='add_coins'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'), 
]