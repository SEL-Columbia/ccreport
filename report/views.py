# encoding=utf-8
# maintainer: katembu

from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _, ugettext

from report.models import CommcareReportURL

@login_required()
def index(request):
    '''Landing page '''
    context = {'title': _(u"Report Dashboard")}
    
    context.update({'report': CommcareReportURL.objects.all()});
    
    return render(request, "home.html", context)
    

def login_greeter(request):

    from django.contrib.auth.views import login
    context = ''
    
    return login(request, template_name='login.html', extra_context=context)
