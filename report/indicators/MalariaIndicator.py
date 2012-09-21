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

from django.utils.translation import ugettext as _
from indicator import Percentage
from report.bamboo import *


class MalariaIndicator():

    def __init__(self, report=None):
        if report is not None:
            self.report = report

    @classmethod
    def uncomplicatedfever_rdt(cls, report):
        '''
        A1
        Number of Under-5's with uncomplicated fever (no other danger signs)
        AND recieved RDT test
        '''
        query='{"danger_sign":"fever","$or":[{"rdt_result":"positive"},{"rdt_result":"negative"}]}'
        try:
            ans = len(bamboo_query(report, query=query))
        except:
            ans = 0
            
        return ans

    @classmethod
    def fever(cls, report):
        '''
        A1
        Number of Under-5's with fever AND no other danger signs
        '''
        query = '{"danger_sign":"fever"}'
        select = '{"danger_sign": 1}'
        try:
            ans = len(bamboo_query(report, query=query))
        except:
            ans = 0
            
        return ans

    @classmethod
    def uncomplicatedfever_rdt_positive(cls, report):
        '''
        A1
        Number of Under-5's with fever AND no other danger signs AND
        recieved RDT test AND RDT positive
        '''
        query='{"danger_sign":"fever","rdt_result":"positive"}'
        try:
            ans = len(bamboo_query(report, query=query))
        except:
            ans = 0
            
        return ans

    @classmethod
    def rdt_positive_antimalarial(cls, report):
        '''
        Number of Under-5's with positive RDT result AND received
        antimalarial/ACT medication
        '''        
        query='{"danger_sign":"fever","rdt_result":"positive"}'
        try:
            ans = len(bamboo_query(report, query=query))
        except:
            ans = 0
            
        return ans

    @classmethod
    def uncomplicatedfever_rdt_notavailable(cls, report):
        '''
        Number of Under-5's with uncomplicated fever (no other danger signs) 
        AND 'RDT Not Available'
        '''
        query='{"danger_sign":"fever","rdt_result":"rdt_not_conducted"}'
        try:
            ans = len(bamboo_query(report, query=query))
        except:
            ans = 0
            
        return ans

    @classmethod
    def fever_rdt_positive_indicator(cls, report):
        '''
        A1
        Proportion of Under-5's with uncomplicated fever who recieved
        RDT test and were RDT positive
        '''
        x = int(cls.uncomplicatedfever_rdt(report))
        y = int(cls.uncomplicatedfever_rdt_positive(report))
        return Percentage(x, y)

    @classmethod
    def fever_rdt_indicator(cls, report):
        '''
        A1
        Proportion of Under-5's with uncomplicated fever who
        recieved RDT test
        '''
        x = int(cls.uncomplicatedfever_rdt(report))
        y = int(cls.fever(report))
        try:
            ans = Percentage(x, y)
        except:
            ans = 0
        return ans

    @classmethod
    def anti_malarial_indicator(cls, report):
        '''
        A1
        Proportion of Under-5's with positive RDT result who
        received antimalarial/ADT medication
        '''
        x = int(cls.rdt_positive_antimalarial(report))
        y = int(cls.uncomplicatedfever_rdt_positive(report))
        try:
            ans = Percentage(x, y)
        except:
            ans = 0
        return ans

    @classmethod
    def fever_rdt_notavailable_indicator(cls, report):
        '''
        A1
        Proportion of Under-5's with uncomplicated fever who did NOT
        receive RDT test due to 'RDT not available' with CHW
        '''
        x = int(cls.uncomplicatedfever_rdt_notavailable(report))
        y = int(cls.fever(report))
        try:
            ans = Percentage(x, y)
        except:
            ans = 0
        return ans

    @classmethod
    def report_indicators(cls, report):
        return (
        {
            'title': _("Malaria"),
            'columns': [
                {'name': _("Uncomplicated fever/recieved RDT test"),
                            'ind': cls.fever_rdt_indicator(report)},
                {'name': _("Positive RDT/Received Anti Malarial"), \
                            'ind': cls.anti_malarial_indicator(report)},
                {'name': _("Uncomplicated/RDT not available"), \
                            'ind': cls.fever_rdt_notavailable_indicator(report)}
            ]
        },
        )
