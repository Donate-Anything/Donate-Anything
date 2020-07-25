from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from donate_anything.charity.forms import BusinessForm, OrganizationForm
from donate_anything.charity.models import (
    BusinessApplication,
    Charity,
    OrganizationApplication,
)


def organization(request, pk):
    charity = get_object_or_404(Charity, id=pk)
    context = {
        "name": charity.name,
        "description": charity.description,
        "how_to_donate": charity.how_to_donate,
    }
    return render(request, "organization/organization.html", context)


@login_required
def applied_organization(request, pk):
    obj = get_object_or_404(OrganizationApplication, id=pk)
    context = {"obj": obj}
    if request.user == obj.applier:
        context["form"] = OrganizationForm(
            instance=obj, initial={"social_media": obj.extra["social_media"]}
        )
    return render(request, "organization/apply/view_org.html", context)


@login_required
def applied_business(request, pk):
    obj = get_object_or_404(BusinessApplication, id=pk)
    context = {"obj": obj}
    if request.user == obj.applier:
        context["form"] = BusinessForm(instance=obj)
    return render(request, "organization/apply/view_bus.html", context)
