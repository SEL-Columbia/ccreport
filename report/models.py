# encoding=utf-8
# maintainer: katembu

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext


class Site(models.Model):

	class Meta:
		app_label = "report"
        verbose_name = _(u"MVP Site")
        verbose_name_plural = _(u"MVP Sites")

	slug = models.SlugField(max_length=30, primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True,
                                   verbose_name=_(u"description"),
                                   help_text=_(u"Site"))

	def __unicode__(self):
		return self.name


class CommcareReport(models.Model):

	class Meta:
		app_label = "report"
        verbose_name = _(u"Commcare Report")
        verbose_name_plural = _(u"Commcare Reports")

	STATUS_ACTIVE = 1
	STATUS_INACTIVE = 0
	STATUS_CHOICES = (
		        (STATUS_ACTIVE, _(u"Active")),
		        (STATUS_INACTIVE, _(u"Inactive")))

	status = models.SmallIntegerField(_(u"Status"), choices=STATUS_CHOICES,
                                      default=STATUS_ACTIVE, db_index=True)
	name = models.CharField(max_length = 100, verbose_name=_(u"Report Name"))
	source_url = models.CharField(max_length = 250,
								  verbose_name=_(u"Report URL"))
	dataset_id = models.CharField(max_length = 100, blank=True, null=True)
	updated_on = models.DateTimeField(auto_now=True)
	created_on = models.DateTimeField(_(u"Created on"), db_index=True, 
										auto_now_add=True)
	site = models.ForeignKey(Site, blank=True, null=True)

	def __unicode__(self):
		return self.name


class SitesUser(models.Model):

	class Meta:
		app_label = "report"
        verbose_name = _(u"User")
        verbose_name_plural = _(u"Users")


	site = models.ForeignKey(Site, verbose_name=_(u"Assigned Site"))
	user = models.ForeignKey(User, unique=True, verbose_name=_(u"User"))

	def __unicode__(self):
		return self.user.username


class ReportMetaData(models.Model):
    class Meta:
        app_label = 'report'
        verbose_name = _(u"Report Metadata")
        verbose_name_plural = _(u"Reports Metadata")

    report = models.ForeignKey(CommcareReport)
    key = models.CharField(verbose_name=_("Key"), max_length=50)
    value = models.TextField(verbose_name=_("Value"))
