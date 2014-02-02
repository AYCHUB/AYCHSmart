# coding:utf-8
"""
Ajax custom lookup
@author: Sébastien Renard <Sebastien.Renard@digitalfox.org>
@license: AGPL v3 or newer (http://www.gnu.org/licenses/agpl-3.0.html)
"""

import workflows.utils as wf

from django.utils import formats

from expense.models import Expense
from django.db.models import Q
from ajax_select import LookupChannel


class ExpenseLookup(LookupChannel):
    model = Expense

    def get_query(self, q, request):
        """ return expenses that match query """
        return Expense.objects.filter(Q(description__icontains=q) |
                                      Q(user__first_name__icontains=q) |
                                      Q(user__last_name__icontains=q) |
                                      Q(comment__icontains=q) |
                                      Q(lead__name__icontains=q) |
                                      Q(lead__deal_id__icontains=q) |
                                      Q(lead__client__organisation__company__name__icontains=q))

    def format_match(self, expense):
        """ (HTML) formatted item for displaying item in the dropdown """
        return u"%s (%s %s) - %s" % (expense, expense.user.first_name, expense.user.last_name,
                                     formats.date_format(expense.expense_date))

    def format_item_display(self, expense):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s (%s %s) - %s" % (expense, expense.user.first_name, expense.user.last_name,
                                     formats.date_format(expense.expense_date))


class ChargeableExpenseLookup(ExpenseLookup):
    def get_query(self, q, request):
        """Only return chargeable expenses that are not already been associated to a client bill"""
        expenses = super(ChargeableExpenseLookup, self).get_query(q, request)
        return expenses.filter(chargeable=True, clientbill=None)


class PayableExpenseLookup(ExpenseLookup):
    def get_query(self, q, request):
        """Only return expenses that can be paid"""
        expenses = super(PayableExpenseLookup, self).get_query(q, request)
        expenses = expenses.filter(workflow_in_progress=True, corporate_card=False, expensePayment=None)
        return [expense for expense in expenses if wf.get_state(expense).transitions.count() == 0]
