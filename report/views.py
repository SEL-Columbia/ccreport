# encoding=utf-8
# maintainer: katembu
import requests
import json

from requests.exceptions import ConnectionError
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, \
    HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _
from report.forms import CommcareReportForm
from report.indicators import get_indicator_list

from report.models import CommcareReport, ReportMetaData
from report.utils import download_commcare_zip_report
from report.bamboo import bamboo_query, bamboo_store_csv_file
from report.utils import dump_json
from report.indicators.MalariaIndicator import MalariaIndicator


@login_required
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
        csv_file = None
        try:
            csv_file = download_commcare_zip_report(
                report.source_url,
                username=settings.COMMCARE_USERNAME,
                password=settings.COMMCARE_PASSWORD)
        except ConnectionError:
            request.session['error_msg'] =\
                _(u"Connection Error: Unable to download report from %s." %
                  report.source_url)
        if csv_file is not None:
            # push the data to bamboo.io
            data = bamboo_store_csv_file(csv_file, settings.BAMBOO_POST_URL)
            if type(data) == dict:
                report.dataset_id = data["id"]
                report.save()
            # TODO: delete csv file or cache
        else:
            return HttpResponse(_(u"Unable to download report!"))
    if request.is_ajax():
        return HttpResponse(u"OK")
    else:
        return HttpResponseRedirect(reverse(index))
    

@login_required
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
@login_required
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

        
@login_required
def indicator(request, report_id):
    try:
        report = CommcareReport.objects.get(pk=report_id)
    except CommcareReport.DoesNotExist: 
        return HttpResponse(_(u"Report not available"))

    #GET SELECT VALUES key
    m = MalariaIndicator(report)
    context = {"mm": m.report_indicators()}
    return render(request, "indicator.html", context)


@login_required
def report(request, report_id):
    context = RequestContext(request)
    report = get_object_or_404(CommcareReport, pk=report_id)
    if request.POST:
        indicator = request.POST.get('indicator', None)
        if indicator is not None:
            meta_data, created = ReportMetaData.objects.get_or_create(
                report=report, key='indicator', value=indicator)
            meta_data.save()
    indicators = ReportMetaData.objects.filter(
        report=report, key="indicator").values_list('value', flat=True)
    indicator_list = get_indicator_list()
    context.indicators = \
        [item for item in indicator_list if item['name'] in indicators]
    # do not include already assigned indicators
    indicator_list =\
        [item for item in indicator_list if item['name'] not in indicators]
    context.indicator_list = indicator_list
    context.report = report
    return render(request, 'report.html', context_instance=context)
