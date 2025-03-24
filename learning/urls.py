from django.urls import path
from .views import learning_resources_view, upload_resource, view_ebook, pay_for_ebook

urlpatterns = [
    path('learning-resources/', learning_resources_view, name='learning_resources'),
    path('upload-resource/', upload_resource, name='upload_resource'),
    path('view-ebook/<uuid:uuid>/', view_ebook, name='view_ebook'),
    path('get-ebook/paid/<uuid:uuid>/', pay_for_ebook, name='get_resources'),
]
