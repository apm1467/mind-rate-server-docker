from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from mind_rate_server.survey.forms import LoginForm
from mind_rate_server.survey import views

urlpatterns = [
    url(r'', include('mind_rate_server.survey.urls')),

    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS

    # redirect admin logout page
    url(r'^admin/logout/', auth_views.logout, {'next_page': '/login'}, name='logout'),

    url(r'^admin/', admin.site.urls),

    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html',
                                        'authentication_form': LoginForm}, name='login'),

    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'),

    url(r'^accounts/', include('registration.backends.hmac.urls')),

    url(r'^study/(?P<study_id>\d+)/$', views.view_answers, name='view_answers'),

    # To define a study-downloading url
    # url(r'^download/(?P<study_id>[1-9][0-9]*)$', views.view_download, name='view_download'),

    # url(r'^preview/(?P<questionnaire_id>\d+)/$', views.preview, name='preview'),

    url(r'^_nested_admin/', include('nested_admin.urls')),
]
