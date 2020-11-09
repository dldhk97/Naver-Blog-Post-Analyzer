from django.conf.urls import url

from . import views

urlpatterns = [
    url('user/analyzedinfo/get', views.get_analyzed_info, name='user/analyzedinfo/get'),
    url('user/keyword/get', views.get_keywords, name='user/keyword/get'),
    
    url('user/feedback/create', views.create_feedback, name='user/feedback/create'),
    url('admin/feedback/get', views.get_feedbacks, name='admin/feedback/get'),
    url('admin/feedback/delete', views.delete_feedback, name='admin/feedback/delete'),

    url('admin/ban/ban', views.ban_ip, name='admin/ban/ban'),
    url('admin/ban/get', views.get_banned_ip, name='admin/ban/get'),
    url('admin/ban/unban', views.unban_ip, name='admin/ban/unban'),

    url('admin/model/learn', views.learn_model, name='admin/model/learn'),
    url('admin/model/load', views.load_model, name='admin/model/load'),
    url('admin/model/save', views.save_model, name='admin/model/save'),

    url('admin/test/authorization', views.authorization, name='admin/test/authorization'),
    url('admin/test/lorem_analyze', views.lorem_analyze, name='admin/test/lorem_analyze'),
    url('admin/test/getanalyzedinfo', views.get_analyzed_info, name='admin/test/getanalyzedinfo'),
    url('admin/test/crawlsingleblog', views.crawl_single_blog, name='admin/test/crawlsingleblog'),
    url('admin/test/crawlsingleblogmedia', views.crawl_single_blog_multimedia, name='admin/test/crawlsingleblogmedia'),
]