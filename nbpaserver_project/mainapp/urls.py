from django.conf.urls import url

from . import views

urlpatterns = [
    url('get', views.get_analyzed_info, name='get'),
]