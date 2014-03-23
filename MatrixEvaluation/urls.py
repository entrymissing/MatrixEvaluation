from django.conf.urls import patterns, include, url
from evalServer import views
from django.conf import settings
from django.contrib.auth.views import login

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^viewSubmissions$', views.viewSubmissions, name='viewSubmissions'),
    url(r'^$', views.frontPage, name='frontPage'),
    url(r'^integrityCheck/(?P<submission_id>\d+)$', views.integrityCheck, name='integrityCheck'),
    url(r'^interface/submitIntegrityCheck$', views.submitIntegrityCheck, name='submitIntegrityCheck'),
    url(r'^interface/setCookie$', views.setCookie, name='setCookie'),
    url(r'^interface/submitAnswer$', views.submitAnswer, name='submitAnswer'),
    url(r'^checkStatus$', views.checkStatus, name='checkStatus'),
    url(r'^viewAccepted$', views.viewAccepted, name='viewAccepted'),
    
    url(r'^adminTools/updateDB$', views.updateDB, name='updateDB'),
    url(r'^login$', views.loginUser, name='loginUser'),
    url(r'^nextPuzzle$', views.nextPuzzle, name='nextPuzzle'),
    url(r'^completed$', views.completed, name='completed'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login', login, {'template_name': 'login.html'}),
    url(r'^accounts/logout', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}),

)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))