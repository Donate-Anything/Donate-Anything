from typing import Iterable

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView

from donate_anything.charity.models.charity import Charity
from donate_anything.item.forms import ModifyItemsForm
from donate_anything.item.models.category import CATEGORY_TYPES, Category
from donate_anything.item.models.item import Item, ProposedItem, WantedItem


# TODO Add django-ratelimit and develop debounce method
def search_item_autocomplete(request):
    """Simple autocomplete for all existing items.
    """
    # TODO Migrate to elasticsearch once there's enough items
    # TODO Use websockets instead since elasticsearch-dsl supports asyncio
    query = request.GET.get("q", None)
    if query is None:
        raise Http404(_("You must specify a query"))
    queryset = (
        Item.objects.defer("is_appropriate")
        .filter(name__icontains=str(query), is_appropriate=True)
        .values_list("id", "name", "image")[:15]
    )
    return JsonResponse(data={"data": list(queryset)})


def _paginate_via_charity(
    queryset,
    page_number: int = 1,
    page_limit: int = 25,
    values_list: Iterable[str] = (
        "charity__id",
        "charity__name",
        "charity__description",
    ),
) -> dict:
    paginator = Paginator(
        list(queryset.select_related("charity").values_list(*values_list)), page_limit,
    )
    # Can't raise error since Django makes sures there's always one page...
    # Even on an empty page or a string page...
    page_obj = paginator.get_page(page_number)
    return {"data": page_obj.object_list, "has_next": page_obj.has_next()}


# Filter and return organizations
_range_length_of_categories = range(len(CATEGORY_TYPES))


def search_category(request, category_type: int):
    try:
        assert category_type in _range_length_of_categories
    except AssertionError:
        raise Http404(_("You must specify a category."))
    return JsonResponse(
        _paginate_via_charity(
            Category.objects.filter(category=category_type), request.GET.get("page"),
        )
    )


def search_item(request, pk: int):
    """Shows charities that can fulfill the selected items
    within the current page.
    """
    return JsonResponse(
        _paginate_via_charity(
            WantedItem.objects.filter(item_id=pk), request.GET.get("page"),
        )
    )


def search_multiple_items(request):
    """View for searching multiple items.
    Returns a completely new HTML template, designed
    specifically for showing which organizations can
    fulfill the most items.
    :return List of charities in order of organizations
    that can take the most inputted items with which items
    are allowed.
    """
    try:
        page_number = int(request.GET.get("page", 1))
        item_ids = set(int(x) for x in request.GET.getlist("q"))
    except (TypeError, ValueError):
        raise Http404(_("You must specify the item IDs."))

    # Load all charities that can fulfill any item asked for.
    # FIXME Multi-search has to practically load an entire database
    #  because organizations can have thousands of WantedItems.
    #  There is a fix: Trigram and marking items as duplicates.
    #  Follow GH #3 https://github.com/Donate-Anything/Donate-Anything/issues/3
    # Or you can just find a better query :P
    queryset = WantedItem.objects.filter(item_id__in=item_ids).values_list(
        "charity_id", "item_id"
    )
    charity_fulfillment: dict = {}
    for obj in queryset:
        try:
            charity_fulfillment[obj[0]].append(obj[1])
        except KeyError:
            charity_fulfillment[obj[0]] = [obj[1]]
    charity_fulfillment = {
        k: v
        for k, v in sorted(
            charity_fulfillment.items(), key=lambda x: len(x[1]), reverse=True
        )
    }
    # Get the charity IDs that are paginated.
    paginator = Paginator(list(charity_fulfillment.keys()), 25,)
    page_obj = paginator.get_page(page_number)
    # Memory management: remove all that are not a part of this list.
    charity_fulfillment = {k: charity_fulfillment[k] for k in page_obj.object_list}

    # Get the charities themselves and extend into array
    for c_id, name, description in Charity.objects.filter(
        id__in=charity_fulfillment.keys()
    ).values_list("id", "name", "description"):
        charity_fulfillment[c_id].extend([name, description[:150]])

    context = {
        "data": charity_fulfillment,
        "page_obj": page_obj,
    }

    return render(request, "organization/multiple_orgs.html", context=context)


def list_active_entity_items(request, charity_id):
    """Lists the items that an active entity can fulfill.
    Returns item names, paginated.
    """
    # Using an index on both entity and item FKs makes
    # the query slightly faster. But negligent.
    """
    QS Timing: 0.07431996694600161 w/ Select related + name
    QS Timing: 0.0004472580919982647 w/ sr + id
    QS Timing: 0.000249934839003231 w/o sr + name
    QS Timing: 0.00010671574200080158 w/o sr + id
    QS Timing: 1.2065899000049285e-05 w/ index on entity and item field
    QS Timing: 2.615080998225494e-06
    QS Timing: 2.5512770001796523e-06
    QS Timing: 3.3379649991047698e-06
    """
    if Charity.objects.filter(id=charity_id).exists():
        # Apparently using select/prefetch_related("item") makes it 10x slower
        qs = (
            WantedItem.objects.only("item__name")
            .filter(charity_id=charity_id)
            .order_by("item__name")
            .values_list("item__name", flat=True)
        )
    else:
        raise Http404
    paginator = Paginator(qs, 50)
    try:
        num = paginator.validate_number(request.GET.get("page", 1))
    except (EmptyPage, PageNotAnInteger):
        raise Http404
    page_obj = paginator.page(num)
    return JsonResponse({"data": list(page_obj.object_list)})


def list_org_items_view(request, entity_id):
    """View that renders the initial items list
    """
    obj = get_object_or_404(Charity, id=entity_id)
    return render(
        request, "organization/list_item.html", {"id": entity_id, "name": obj.name}
    )


def list_proposed_existing_item(request, proposed_item_pk):
    proposed_item_obj = get_object_or_404(ProposedItem, id=proposed_item_pk)
    paginator = Paginator(proposed_item_obj.item, 50)
    try:
        num = paginator.validate_number(request.GET.get("page", 1))
    except (EmptyPage, PageNotAnInteger):
        raise Http404
    page_obj = paginator.page(num)
    qs = (
        Item.objects.only("id", "name")
        .filter(id__in=page_obj.object_list, is_appropriate=True)
        .order_by("id")
    )
    return JsonResponse({"data": [(x.id, x.name) for x in qs]})


def list_org_proposed_item_view(request, proposed_item_pk):
    """View that renders the initial proposed items list
    Lists all names and item IDs along with entity ID and name
    """
    obj = get_object_or_404(
        ProposedItem.objects.select_related("entity"), id=proposed_item_pk
    )
    return render(
        request,
        "organization/suggest/list_proposed_item.html",
        {
            "proposed_item": obj,
            "can_edit": (request.user == obj.user and not obj.closed),
        },
    )


# Only need requires_csrf_token when it's a form in template view
@method_decorator(csrf_protect, name="dispatch")
class ProposedItemFormView(LoginRequiredMixin, FormView):
    """Form view for proposed item fill out."""

    form_class = ModifyItemsForm

    def form_valid(self, form):
        # Prepare data:
        item = form.cleaned_data["item"]
        names = form.cleaned_data["names"]

        # Determine if create or update
        if form.cleaned_data["id"] is None:
            # User is redirected to forum
            ProposedItem.objects.create(
                user=self.request.user,
                entity_id=form.cleaned_data["entity"],
                item=item,
                names=names,
            )
            messages.add_message(
                self.request,
                messages.INFO,
                _(
                    "Your proposed items have been posted! You can "
                    "enter the link in the forum to check out others' "
                    "opinions on the proposition. You can follow the "
                    "link to edit your proposition later on."
                ),
            )
        else:
            ProposedItem.objects.filter(
                id=form.cleaned_data["id"], user=self.request.user
            ).update(item=item, names=names)
        return HttpResponse()

    def form_invalid(self, form):
        return JsonResponse({"errors": form.errors}, status=400)


proposed_item_form_view = ProposedItemFormView.as_view()
