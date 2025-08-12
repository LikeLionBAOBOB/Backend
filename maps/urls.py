from django.urls import path
from .views import *

app_name = 'maps'

urlpatterns = [
        path('nearby/', NearbyLibrariesView.as_view(), name='libraries-nearby'), 
]