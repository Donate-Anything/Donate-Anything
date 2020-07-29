from typing import Iterable

from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from donate_anything.charity.models.charity import Charity
from donate_anything.item.models.category import CATEGORY_TYPES, Category
from donate_anything.item.models.item import Item, WantedItem


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
