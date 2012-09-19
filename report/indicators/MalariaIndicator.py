# encoding=utf-8
# maintainer: katembu
'''
Generate Malaria indicators
PASS object: Report 
All elements in report type should be mapped to:
Danger sign = danger_sign
    choices = fever
RDT results = rdt_results
    choices = positive, negative, not_available
Encounter Date = encounter_date
'''

from django.utils.translation import ugettext_lazy as _, ugettext
from report.models import *
from report.bamboo import *


class MalariaIndicator():

    def __init__(self, report):
        self.report = report

    def uncomplicatedfever_rdt(self):
        '''
        A1
        Number of Under-5's with uncomplicated fever (no other danger signs)
        AND recieved RDT test
        '''
        query='{"danger_sign":"fever","$or":[{"rdt_result":"positive"},{"rdt_result":"negative"}]}'
        try:
            ans = len(bamboo_query(self.report, query=query))
        except:
            ans = 0
            
        return ans

    def fever(self):
        '''
        A1
        Number of Under-5's with fever AND no other danger signs
        '''
        query = '{"danger_sign":"fever"}'
        select = '{"danger_sign": 1}'
        try:
            ans = len(bamboo_query(self.report, query=query))
        except:
            ans = 0
            
        return ans
        
    def uncomplicatedfever_rdt_positive(self):
        '''
        A1
        Number of Under-5's with fever AND no other danger signs AND
        recieved RDT test AND RDT positive
        '''
        query='{"danger_sign":"fever","rdt_result":"positive"}'
        try:
            ans = len(bamboo_query(self.report, query=query))
        except:
            ans = 0
            
        return ans

    def rdt_positive_antimalarial(self):
        '''
        Number of Under-5's with positive RDT result AND received
        antimalarial/ACT medication
        '''        
        query='{"danger_sign":"fever","rdt_result":"positive"}'
        try:
            ans = len(bamboo_query(self.report, query=query))
        except:
            ans = 0
            
        return ans

    def uncomplicatedfever_rdt_notavailable(self):
        '''
        Number of Under-5's with uncomplicated fever (no other danger signs) 
        AND 'RDT Not Available'
        '''
        query='{"danger_sign":"fever","rdt_result":"rdt_not_conducted"}'
        try:
            ans = len(bamboo_query(self.report, query=query))
        except:
            ans = 0
            
        return ans
     
    def fever_rdt_positive_indicator(self):
        '''
        A1
        Proportion of Under-5's with uncomplicated fever who recieved
        RDT test and were RDT positive
        '''
        x = float(self.uncomplicatedfever_rdt())
        x = float(self.uncomplicatedfever_rdt_positive())
        return int(x/y*100)

    def fever_rdt_indicator(self):
        '''
        A1
        Proportion of Under-5's with uncomplicated fever who
        recieved RDT test
        '''
        x = float(self.uncomplicatedfever_rdt())
        y = float(self.fever())
        try:
            ans = int(x/y*100)
        except:
            ans = 0
        return int(ans)

    def anti_malarial_indicator(self):
        '''
        A1
        Proportion of Under-5's with positive RDT result who
        received antimalarial/ADT medication
        '''
        x = float(self.rdt_positive_antimalarial())
        y = float(self.uncomplicatedfever_rdt_positive())
        try:
            ans = int(x/y*100)
        except:
            ans = 0
        return int(ans)

    def fever_rdt_notavailable_indicator(self):
        '''
        A1
        Proportion of Under-5's with uncomplicated fever who did NOT
        receive RDT test due to 'RDT not available' with CHW
        '''
        x = float(self.uncomplicatedfever_rdt_notavailable())
        y = float(self.fever())
        try:
            ans = int(x/y*100)
        except:
            ans = 0
        return int(ans)
   
    def report_indicators(self):
        return (
        {
            'title': _("Malaria"),
            'columns': [
                {'name': _("Uncomplicated fever/recieved RDT test"),
                            'ind': self.fever_rdt_indicator()},
                {'name': _("Positive RDT/Received Anti Malarial"), \
                            'ind': self.anti_malarial_indicator()},
                {'name': _("Uncomplicated/RDT not available"), \
                            'ind': self.fever_rdt_notavailable_indicator()}
            ]
        },
        )
