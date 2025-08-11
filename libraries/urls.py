from django.urls import path
from .views import *

app_name = 'libraries'

urlpatterns = [
    path('<int:lib_code>/simple/', LibrarySimpleView.as_view(), name='simple-library'),  # /libraries/<int: library_id>/simple/ -> library_id에 lib_code 입력하면 됨
    path('<int:lib_code>/detail/', LibraryDetailView.as_view(), name='detail-library'),  # /libraries/<int: library_id>/detail/ -> library_id에 lib_code 입력하면 됨
]