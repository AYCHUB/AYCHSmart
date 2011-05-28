# coding: utf-8
"""
Pydici core views. Http request are processed here.
@author: Sébastien Renard (sebastien.renard@digitalfox.org)
@license: GPL v3 or newer
"""

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Q

from pydici.leads.models import Lead
from pydici.people.models import Consultant, SalesMan
from pydici.crm.models import ClientCompany, ClientContact
from pydici.staffing.models import Mission
from pydici.billing.models import Bill


@login_required
def index(request):

    request.session["mobile"] = False

    myLeadsAsResponsible = set()
    myLatestArchivedLeads = set()
    myLeadsAsStaffee = set()

    consultants = Consultant.objects.filter(trigramme__iexact=request.user.username)
    if consultants:
        consultant = consultants[0]
        myLeadsAsResponsible = set(consultant.lead_responsible.active().select_related())
        myLeadsAsStaffee = consultant.lead_set.active().select_related()
        myLatestArchivedLeads = set((consultant.lead_responsible.passive().select_related().order_by("-update_date")
                                  | consultant.lead_set.passive().select_related().order_by("-update_date"))[:10])

    salesmen = SalesMan.objects.filter(trigramme__iexact=request.user.username)
    if salesmen:
        salesman = salesmen[0]
        myLeadsAsResponsible.update(salesman.lead_set.active().select_related())
        myLatestArchivedLeads.update(salesman.lead_set.passive().select_related().order_by("-update_date")[:10])


    latestLeads = Lead.objects.all().select_related().order_by("-update_date")[:10]

    return render_to_response("core/index.html",
                              {"latest_leads": latestLeads,
                               "my_leads_as_responsible": myLeadsAsResponsible,
                               "my_leads_as_staffee": myLeadsAsStaffee,
                               "my_latest_archived_leads": myLatestArchivedLeads,
                               "user": request.user },
                               RequestContext(request))



@login_required
def mobile_index(request):
    """Mobile device index page"""
    # Mark session as "mobile"
    request.session["mobile"] = True
    consultant = Consultant.objects.get(trigramme__iexact=request.user.username)
    companies = ClientCompany.objects.filter(clientorganisation__client__lead__mission__timesheet__consultant=consultant).distinct()
    return render_to_response("core/m.index.html",
                              {"user": request.user,
                               "consultant" : consultant,
                               "companies" : companies },
                              RequestContext(request))

@login_required
def search(request):
    """Very simple search function on all major pydici objects"""

    consultants = None
    clientCompanies = None
    leads = None
    missions = None
    clientContacts = None
    bills = None

    words = request.GET.get("q", "")
    words = words.split()

    if words:
        # Consultant
        if request.GET.get("consultant"):
            consultants = Consultant.objects.filter(active=True)
            for word in words:
                consultants = consultants.filter(Q(name__icontains=word) |
                                                 Q(trigramme__icontains=word))
            consultants = consultants.distinct()

        # Client Company
        if request.GET.get("company"):
            clientCompanies = ClientCompany.objects.all()
            for word in words:
                clientCompanies = clientCompanies.filter(name__icontains=word)
            clientCompanies = clientCompanies.distinct()

        # Client contact
        if request.GET.get("contact"):
            clientContacts = ClientContact.objects.all()
            for word in words:
                clientContacts = clientContacts.filter(name__icontains=word)
            clientContacts = clientContacts.distinct()

        # Leads
        if request.GET.get("lead"):
            leads = Lead.objects.all()
            for word in words:
                leads = leads.filter(Q(name__icontains=word) |
                                     Q(description__icontains=word) |
                                     Q(tags__name__iexact=word) |
                                     Q(client__contact__name__icontains=word) |
                                     Q(client__organisation__company__name__icontains=word) |
                                     Q(client__organisation__name__iexact=word) |
                                     Q(deal_id__icontains=word[:-1])) # Squash last letter that could be mission letter
            leads = leads.distinct()

        # Missions
        if request.GET.get("mission"):
            missions = Mission.objects.filter(active=True)
            for word in words:
                missions = missions.filter(Q(deal_id__icontains=word) |
                                           Q(description__icontains=word))

            # Add missions from lead
            if leads:
                missions = set(missions)
                for lead in leads:
                    for mission in lead.mission_set.all():
                        missions.add(mission)
                missions = list(missions)

        # Bills
        if request.GET.get("bill"):
            bills = Bill.objects.all()
            for word in words:
                bills = bills.filter(Q(bill_id__icontains=word) |
                                     Q(comment__icontains=word))

            # Add bills from lead
            if leads:
                bills = set(bills)
                for lead in leads:
                    for bill in lead.bill_set.all():
                        bills.add(bill)
            # Sort
            bills = list(bills)
            bills.sort(key=lambda x: x.creation_date)

    return render_to_response("core/search.html",
                              {"query" : " ".join(words),
                               "consultants": consultants,
                               "client_companies" : clientCompanies,
                               "client_contacts" : clientContacts,
                               "leads" : leads,
                               "missions" : missions,
                               "bills" : bills,
                               "user": request.user },
                               RequestContext(request))

def internal_error(request):
    """Custom internal error view.
    Like the default builtin one, but with context to allow proper menu display with correct media path"""
    return render_to_response("500.html", {}, RequestContext(request))
