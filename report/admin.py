# encoding=utf-8
# maintainer: katembu

from django.contrib import admin
from django.contrib.auth.models import User

from report.models import Site, CommcareReport, ReportMetaData, SitesUser

admin.site.register(Site)
admin.site.register(CommcareReport)
admin.site.register(ReportMetaData)

admin.site.unregister(User)
admin.site.register(SitesUser)
