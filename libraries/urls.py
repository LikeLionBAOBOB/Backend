from django.urls import path
from .views import *

app_name = 'libraries'

urlpatterns = [
    path('<int:lib_code>/simple/', LibrarySimpleView.as_view(), name='simple-library'),  # /libraries/<int: library_id>/simple/ -> library_id에 lib_code 입력하면 됨
]