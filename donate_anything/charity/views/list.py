from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from donate_anything.charity.forms import (
    BusinessForm,
    ExistingSuggestEditForm,
    OrganizationForm,
    SuggestedEditForm,
)
from donate_anything.charity.models import (
    AppliedBusinessEdit,
    AppliedOrganizationEdit,
    BusinessApplication,
    Charity,
    OrganizationApplication,
)
from donate_anything.users.models.charity import VerifiedAccount


def organization(request, pk):
    charity = get_object_or_404(Charity, id=pk)
    context = {
        "id": charity.id,
        "name": charity.name,
        "description": charity.description,
        "how_to_donate": charity.how_to_donate,
        "logo": charity.logo,
    }
    user = request.user
    if user.is_authenticated:
        context["suggest_edit_form"] = ExistingSuggestEditForm(
            initial={**context, "link": charity.link}
        )
        context["is_verified_account"] = VerifiedAccount.objects.filter(
            charity=charity, user=user
        ).exists()
    return render(request, "organization/organization.html", context)


@login_required
def applied_organization(request, pk):
    obj = get_object_or_404(OrganizationApplication, id=pk)
    context = {"obj": obj}
    if request.user == obj.applier:
        context["form"] = OrganizationForm(
            instance=obj, initial={"social_media": obj.extra.get("social_media", "")}
        )
    else:
        context["suggest_form"] = SuggestedEditForm()
    return render(request, "organization/apply/view_org.html", context)


@login_required
def applied_business(request, pk):
    obj = get_object_or_404(BusinessApplication, id=pk)
    context = {"obj": obj}
    if request.user == obj.applier:
        context["form"] = BusinessForm(instance=obj)
    else:
        context["suggest_form"] = SuggestedEditForm()
    return render(request, "organization/apply/view_bus.html", context)


def _paginate_and_return_json(qs, request) -> JsonResponse:
    """Paginates qs and and checks
    for certain query parameters for
    list organization edits
    """
    unseen = request.GET.get("unseen", False)
    if unseen == "1":
        qs = qs.filter(viewed=False)
    # Already ordered by time since AutoField
    try:
        paginator = Paginator(qs, 25, allow_empty_first_page=False)
        page = request.GET.get("page", 1)
        if int(page) > paginator.num_pages:
            raise EmptyPage
        page_obj = paginator.get_page(page)
    except (EmptyPage, ValueError, TypeError):
        raise Http404()
    if unseen == "1":
        data = {
            "data": [
                [x.id, x.user.get_username(), x.edit, x.created, x.updated]
                for x in page_obj.object_list
            ]
        }
    else:
        data = {
            "data": [
                [x.id, x.user.get_username(), x.edit, x.created, x.updated, x.viewed]
                for x in page_obj.object_list
            ]
        }
    return JsonResponse(data=data)


@login_required
def applied_organization_edits(request, pk):
    """Returns suggested edits for OrganizationApplications
    using Paginator. Returns username, edit, datetime
    """
    qs = (
        AppliedOrganizationEdit.objects.select_related("user")
        .filter(proposed_entity_id=pk)
        .order_by("id")
    )
    return _paginate_and_return_json(qs, request)


@login_required
def applied_business_edits(request, pk):
    """Returns suggested edits for BusinessApplications
    using Paginator. Returns username, user pk, edit, created+updated
    """
    qs = (
        AppliedBusinessEdit.objects.select_related("user")
        .filter(proposed_entity_id=pk)
        .order_by("id")
    )
    return _paginate_and_return_json(qs, request)


def _mark_view(user_id: int, obj):
    if obj.proposed_entity.applier_id != user_id:
        return HttpResponseForbidden(
            _("You must be the applicant to mark a suggestion as viewed.")
        )
    obj.viewed = not obj.viewed
    obj.save(update_fields=["viewed"])
    return HttpResponse()


@login_required
def viewed_org_edit(request, edit_pk: int):
    """Mark an organization edit as viewed.
    Reversible
    """
    obj = get_object_or_404(AppliedOrganizationEdit, id=edit_pk)
    return _mark_view(request.user.id, obj)


@login_required
def viewed_bus_edit(request, edit_pk: int):
    """Mark a business edit as viewed.
    Reversible
    """
    obj = get_object_or_404(AppliedBusinessEdit, id=edit_pk)
    return _mark_view(request.user.id, obj)


class CommunityListView(ListView):
    model = Charity
    paginate_by = 100
    template_name = "organization/list.html"

    def get_queryset(self):
        return Charity.objects.only("id", "name").order_by("id")


all_entities_list_view = CommunityListView.as_view()


def search_organization_autocomplete(request):
    query = request.GET.get("q", None)
    if query is None:
        raise Http404(_("You must specify a query"))
    queryset = Charity.objects.filter(name__icontains=str(query)).values_list(
        "id", "name"
    )[:15]
    return JsonResponse(data={"data": list(queryset)})
