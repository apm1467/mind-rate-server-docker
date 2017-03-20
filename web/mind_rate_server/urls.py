from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from mind_rate_server.survey.forms import LoginForm
from mind_rate_server.survey import views
from django.views.generic import RedirectView

urlpatterns = [
    url(r'', include('mind_rate_server.survey.urls')),

    url(r'^grappelli/', include('grappelli.urls')),

    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html',
                                        'authentication_form': LoginForm}, name='login'),

    # send user to /login after logged out
    url(r'^admin/logout/', auth_views.logout, {'next_page': '/login'}, name='logout'),

    # redirect admin/login to /login
    url(r'^admin/login/', RedirectView.as_view(pattern_name='login', permanent=True)),

    url(r'^admin/', admin.site.urls),

    url(r'^accounts/', include('registration.backends.hmac.urls')),

    #url(r'^study/(?P<study_id>\d+)/$', views.view_answers, name='view_answers'),

    # download study to app
    url(r'^download/(?P<study_id>[0-9]+)/$', views.download, name='download'),

    url(r'^proband_info/(?P<study_id>[0-9]+)/$', views.download_proband_info_questionnaire),

    # receive answer from app
    url(r'^receive_answer/', views.receive_answer, name='receive_answer'),

    url(r'^preview/(?P<questionnaire_id>\d+)/$', views.preview, name='preview'),

    url(r'^_nested_admin/', include('nested_admin.urls')),
]
