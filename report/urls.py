# encoding=utf-8
# maintainer: katembu

from django.conf.urls import patterns, include, url
from django.contrib import admin
from report import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples
    url(r'^$', views.index, name='dashboard'),
    url(r'^report/?$', views.index),
    url(r'^report/(?P<report_id>[^/]+)/$', 'report.views.report'),
    
    url(r'^login/$', 'report.views.login_greeter', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'logout.html', 'next_page': '/'}, name='logout'),

    url(r'^add-cc-report/?$', 'report.views.add_commcare_report',
        name='add-cc-report'),

    #Single report summary
    url(r'^summary/(?P<report_id>[^/]+)$', 
        'report.views.report_summary', name='summary'),
    url(r'refresh-dataset/(?P<report_pk>\d+)/$',
        'report.views.refresh_dataset', name='refresh-dataset'),
    url(r"report-meta/(?P<report_id>[^/]+)/$", 'report.views.metadata'),
    url(r'^indicator/(?P<report_id>[^/]+)$', 
        'report.views.indicator', name='indicator'),
        
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
