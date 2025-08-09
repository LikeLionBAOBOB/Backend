from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('user/login/', UserLoginView.as_view(), name='user-login'),       # /accounts/user/login/
    path('admin/login/', ManagerLoginView.as_view(), name='manager-login'), # /accounts/admin/login/
]