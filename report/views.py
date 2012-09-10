# encoding=utf-8
# maintainer: katembu

from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _, ugettext


def index(request):
    '''Landing page '''
    context = {'title': _(u"Report Dashboard")}

    return render(request, "home.html", context)
