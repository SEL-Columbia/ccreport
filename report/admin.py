# encoding=utf-8
# maintainer: katembu

from django.contrib import admin
from django.contrib.auth.models import User

from report.models import Site, CommcareReportURL, SitesUser

admin.site.register(Site)
admin.site.register(CommcareReportURL)

admin.site.unregister(User)
admin.site.register(SitesUser)
