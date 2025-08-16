from django.urls import path
from .views import *

app_name = 'seats'

urlpatterns = [
    path('<int:lib_code>/', SeatStatusView.as_view(), name='seat_status'),
]