from django.urls import path
from .views import *

app_name = 'adminpanel'

urlpatterns = [
    path('library/', ManagerLibraryView.as_view(), name='manager_library'),     # /adminpanel/library/
]