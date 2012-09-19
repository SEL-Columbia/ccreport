from django.forms import ModelForm
from report.models import CommcareReport

class CommcareReportForm(ModelForm):

    class Meta:
        model = CommcareReport
