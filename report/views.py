# encoding=utf-8
# maintainer: katembu

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _

from report.models import CommcareReport

@login_required()
def index(request):
    '''Landing page '''
    context = RequestContext(request)
    context.commcare_reports = CommcareReport.objects.all()
    context.title = _(u"Report Dashboard")
    return render(request, "home.html", context_instance=context)
    

def login_greeter(request):

    from django.contrib.auth.views import login
    context = ''
    
    return login(request, template_name='login.html', extra_context=context)
