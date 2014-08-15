# -*- coding: UTF-8 -*-
"""URL dispatcher for expense module
@author: Sébastien Renard (sebastien.renard@digitalfox.org)
@license: AGPL v3 or newer (http://www.gnu.org/licenses/agpl-3.0.html)
"""

from django.conf.urls import patterns, url


expense_urls = patterns('expense.views',
                        (r'^$', 'expenses'),
                        (r'^(?P<expense_id>\d+)$', 'expenses'),
                        (r'^(?P<expense_id>\d+)/receipt$', 'expense_receipt'),
                        (r'^(?P<expense_id>\d+)/(?P<transition_id>\w+)', 'update_expense_state'),
                        (r'^mission/(?P<mission_id>\d+)$', 'mission_expenses'),
                        (r'^history/?$', 'expenses_history'),
                        (r'^chargeable/?$', 'chargeable_expenses'),
                        (r'^payment/?$', 'expense_payments'),
                        (r'^payment/(?P<expense_payment_id>\d+)/?$', 'expense_payments'),
                        (r'^payment/(?P<expense_payment_id>\d+)/detail$', 'expense_payment_detail'),
                        )
