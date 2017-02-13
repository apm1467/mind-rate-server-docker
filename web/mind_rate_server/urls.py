"""mind_rate_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from mind_rate_server.survey.forms import LoginForm
from registration.views import RegistrationView
from mind_rate_server.survey import views


urlpatterns = [
    url(r'', include('mind_rate_server.survey.urls')),

    url(r'^admin/', admin.site.urls),

    # url(r'', include('registration.backends.simple.urls')),

    # url(r'^register/$', RegistrationView.as_view(), name='registration_register'),

    # url(r'^signup/$', auth_views.login, {'template_name': 'registration/signup.html',
    #                                     'authentication_form': UserCreationForm}, name='signup'),

    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html',
                                        'authentication_form': LoginForm}, name='login'),

    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'),

    url(r'^accounts/', include('registration.backends.hmac.urls')),

    url(r'^study/(?P<study_id>\d+)/$', views.view_answers, name='view_answers'),
]
