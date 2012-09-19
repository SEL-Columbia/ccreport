# encoding=utf-8
# maintainer: katembu
import requests

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, \
    HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _
from report.forms import CommcareReportForm

from report.models import CommcareReport, ReportMetaData
from report.utils import download_commcare_zip_report
from report.bamboo import bamboo_query
from report.utils import dump_json
from report.indicators.MalariaIndicator import MalariaIndicator
import json


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
            # push the data to bamboo.io
            files = {"csv_file": ('data.csv', open(csv_file))}
            r = requests.post(settings.BAMBOO_POST_URL, files=files)
            if r.status_code == 200:
                content = json.loads(r.content)
                report.dataset_id = content["id"]
                report.save()
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

    #GET SELECT VALUES key
    try:
        select_values = ReportMetaData.objects.get(pk=report_id, 
                                                   key='select_values')
        select = True
        query = bamboo_query(report, select=json.dumps(select_values.value),
                             as_summary=True)
    except ReportMetaData.DoesNotExist:
        query = bamboo_query(report, as_summary=True)
        select = False

    print query
    context = {'report': report,
               'data_dict': query,
               'select': select,
               'data_summary': dump_json(query)}
    return render(request, "summary.html", context)


@require_POST        
@login_required()
def metadata(request, report_id):
    try:
        report = CommcareReport.objects.get(pk=report_id)
    except CommcareReport.DoesNotExist: 
        pass

    fields = request.POST.getlist('select_fields')
    d = { i: 1 for i in fields }

    md = ReportMetaData()
    md.report = report
    md.key = 'select_values'
    md.value = d
    md.save()
    
    return HttpResponseRedirect("/summary/%s" % report_id)


@login_required
def add_commcare_report(request):
    context = RequestContext(request)
    form = CommcareReportForm()
    if request.POST:
        form = CommcareReportForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            url = form.cleaned_data['source_url']
            if not CommcareReport.objects.filter(
                    name=name, source_url=url).count():
                form.save()
                return HttpResponseRedirect(reverse(index))
            else:
                context.error = _(u"There already exists a report with the"
                                  u" same name and url!")
    context.form = form;
    return render(request, "report-form.html", context_instance=context)

        
@login_required()
def indicator(request, report_id):
    print "Pass"
    try:
        report = CommcareReport.objects.get(pk=report_id)
    except CommcareReport.DoesNotExist: 
        pass

    #GET SELECT VALUES key
    m = MalariaIndicator(report)
    context = {"mm": m.report_indicators()}
    return render(request, "indicator.html", context)
