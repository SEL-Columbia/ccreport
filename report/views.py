# encoding=utf-8
# maintainer: katembu

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, \
    HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _

from report.models import CommcareReport
from report.utils import download_commcare_zip_report
from report.bamboo import bamboo_query
from report.utils import dump_json

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


def refresh_dataset(request, report_pk):
    # download the report csv data from commcare
    try:
        report = CommcareReport.objects.get(pk=report_pk)
    except CommcareReport.DoesNotExist:
        return HttpResponseNotFound(_(u"Error: Report Not found!"))
    else:
        csv_file = download_commcare_zip_report(
            report.source_url,
            username=settings.COMMCARE_USERNAME,
            password=settings.COMMCARE_PASSWORD)
        if csv_file is not None:
            pass  # push the data to bamboo.io
            # TODO: delete csv file or cache
        else:
            return HttpResponse(_(u"Unable to download report!"))
    if request.is_ajax():
        return HttpResponse(u"OK")
    else:
        return HttpResponseRedirect(reverse(index))
    

@login_required()
def report_summary(request, report_id):
    
    try:
        report = CommcareReport.objects.get(pk=report_id)
    except CommcareReport.DoesNotExist: 
        pass

    query = bamboo_query(report, as_summary=True)
    context = {'report': report,
               'data_dict': query,
               'data_summary': dump_json(query)}
    return render(request, "summary.html", context)

