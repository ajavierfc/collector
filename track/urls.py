from django.conf.urls import url

from . import views, auths

app_name = 'track'

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^login/$', auths.auth_login, name='auth-login'),
    url(r'^logout/$', auths.auth_logout, name='auth-logout'),
    url(r'^register/$', auths.auth_register, name='auth-register'),

    url(r'^upload-edit/(?P<upload_id>[0-9]*)$', views.upload_edit, name='upload-edit'),
    url(r'^upload-save/(?P<upload_id>[0-9]*)$', views.upload_save, name='upload-save'),
    url(r'^upload-delete/(?P<upload_id>[0-9]+)$', views.upload_delete, name='upload-delete'),
    url(r'^upload/(?P<upload_id>[0-9]+)$', views.upload_view, name='upload-view'),
    url(r'^upload-raw/(?P<upload_id>[0-9]+)$', views.upload_raw, name='upload-raw'),

    url(r'^title-list/$', views.title_list, name='title-list'),
    url(r'^title-edit/(?P<title_id>[0-9]*)$', views.title_edit, name='title-edit'),
    url(r'^title-save/(?P<title_id>[0-9]*)$', views.title_save, name='title-save'),
    url(r'^title-delete/(?P<title_id>[0-9]+)$', views.title_delete, name='title-delete'),
    url(r'^title/(?P<title_id>[0-9]+)$', views.title_view, name='title-view'),

    url(r'^title/(?P<title_id>[0-9]+)/release-edit/(?P<release_id>[0-9]*)$', views.release_edit, name='release-edit'),
    url(r'^title/(?P<title_id>[0-9]+)/release-save/(?P<release_id>[0-9]*)$', views.release_save, name='release-save'),
    url(r'^title/(?P<title_id>[0-9]+)/release-delete/(?P<release_id>[0-9]+)$', views.release_delete, name='release-delete'),
    url(r'^title/(?P<title_id>[0-9]+)/release-upload/(?P<release_id>[0-9]+)$', views.release_upload, name='release-upload'),

    url(r'^release-get-options/$', views.release_get_options, name='release-get-options'),
]
