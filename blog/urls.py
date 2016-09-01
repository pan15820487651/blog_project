
from django.conf.urls import include, url
from django.contrib import admin
from blog.views import index,archive,article,do_login,do_logout,do_reg,comment_post

urlpatterns = [
    url(r'^$',index, name='index'),
    url(r'^archive/$',archive, name='archive'),
    url(r'^article/$',article, name='article'),
    url(r'^login/$',do_login, name='login'),
    url(r'^logout/$',do_logout, name='logout'),
    url(r'^reg', do_reg, name='reg'),
    url(r'^comment/post/$', comment_post, name='comment_post'),
]


