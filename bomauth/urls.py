from django.conf.urls import url

from bomauth import views

urlpatterns = [
   url(r'^$', views.index, name='index'),
   url(r'^login/$', 'django.contrib.auth.views.login', { 'template_name' : 'login.html' }),
   url(r'^logout/$', 'django.contrib.auth.views.logout', { 'template_name' : 'logout.html' }),
   url(r'^register/$', views.register, name='register'),
   url(r'^user/password/reset/$',
         'django.contrib.auth.views.password_reset',
         {'post_reset_redirect' : '/user/password/reset/done/'},
         name="password_reset"),
   url(r'^user/password/reset/done/$',
    'django.contrib.auth.views.password_reset_done'),
   url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
    'django.contrib.auth.views.password_reset_confirm', 
    {'post_reset_redirect' : '/user/password/done/'}),
   url(r'^user/password/done/$', 
    'django.contrib.auth.views.password_reset_complete'),
   url(r'^profile/$', views.profile, name='profile'),
   url(r'^profile/edit', views.update_profile, name='update_profile'),
   ]
