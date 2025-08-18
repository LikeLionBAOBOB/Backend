from django.urls import path
from .views import *

app_name = 'adminpanel'

urlpatterns = [
    path('library/', ManagerLibraryView.as_view(), name='manager_library'),     # /adminpanel/library/
    path('seats/', AdminSeatStatusView.as_view(), name='admin_seats'),
    path('congestion/', AdminCongestionView.as_view(), name='admin_congestion'),
    path('<int:seat_id>/seats/', AdminSeatLogView.as_view(), name='admin_seat_log'),
]