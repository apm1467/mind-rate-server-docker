from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Study


@login_required(login_url="login/")
def home(request):
    user = User.objects.get(username=request.user.username)

    # give user access to the admin site
    user.is_staff = True

    # all permissions of the survey app
    content_type_list = ContentType.objects.filter(app_label='survey')

    for content_type in content_type_list:
        user.user_permissions.add(
            *Permission.objects.filter(content_type__exact=content_type)
        )

    user.save()

    # send user to the admin site
    return redirect('/admin/')


def view_answers(request, study_id):
    study = get_object_or_404(Study, pk = study_id)
    return render(request, 'view_answers.html', {"study":study})
