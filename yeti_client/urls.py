from django.conf import settings
from django.conf.urls import patterns, url
import django.contrib.auth.views
from yeti_client import views

from __init__ import VERSION, CLIENT_NAME


urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^login/$', django.contrib.auth.views.login,
            {
                'template_name': 'login.html',
                'extra_context': {
                    'version': VERSION,
                    'client_name': CLIENT_NAME
                }
            }, name='login'),
        url(r'^logout/$', django.contrib.auth.views.logout_then_login, name='logout'),
        url(r'^history/$', views.history, name='history'),
        url(r'^alerts/$', views.alerts, name='alerts'),
        url(r'^settings/$', views.settings, name='settings'),
        url(r'^push_file/$', views.push_file, name='push_file'),
        url(r'^push_stix_ip/$', views.push_stix_ip, name='push_stix_ip'),
        url(r'^push_stix_email/$', views.push_stix_email, name='push_stix_email'),
        url(r'^pull/$', views.pull, name='pull'),
        (r'^received/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + 'received/'}),
)
