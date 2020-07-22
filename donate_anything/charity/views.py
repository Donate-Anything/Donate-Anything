from django.http import Http404
from django.shortcuts import render

from donate_anything.charity.models.charity import Charity


def organization(request, pk):
    try:
        charity = Charity.objects.get(pk=pk)
    except Charity.DoesNotExist:
        raise Http404()
    context = {
        "name": charity.name,
        "description": charity.description,
        "how_to_donate": charity.how_to_donate,
    }
    return render(request, "pages/organization.html", context)
