from django.conf.urls import url

from . import views

urlpatterns = [
    url('user/analyzedinfo/get', views.get_analyzed_info, name='user/analyzedinfo/get'),
    url('user/keyword/get', views.get_keyword, name='user/keyword/get'),
    url('user/bloginfo/get', views.get_bloginfo, name='user/bloginfo/get'),
    
    url('user/feedback/send', views.send_feedback, name='user/feedback/send'),
    url('admin/feedback/get', views.get_feedbacks, name='admin/feedback/get'),
    url('admin/feedback/delete', views.delete_feedback, name='admin/feedback/delete'),

    url('admin/ban/ban', views.ban_user, name='admin/ban/ban'),
    url('admin/ban/get', views.get_banned_user, name='admin/ban/get'),
    url('admin/ban/unban', views.unban_user, name='admin/ban/unban'),

    url('admin/model/learn', views.learn_model, name='admin/model/learn'),
    url('admin/model/load', views.load_model, name='admin/model/load'),
    url('admin/model/save', views.save_model, name='admin/model/save'),

    url('admin/test/authorization', views.authorization, name='admin/test/authorization'),
    url('admin/test/lorem_analyze', views.lorem_analyze, name='admin/test/lorem_analyze'),
    url('admin/test/getanalyzedinfo', views.get_analyzed_info, name='admin/test/getanalyzedinfo'),
]