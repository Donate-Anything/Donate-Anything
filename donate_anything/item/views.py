from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

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
        .annotate(
            similarity=TrigramSimilarity("name", str(query))
            # TrigramSimilarity and Difference are just opposites
        )
        .filter(similarity__gt=0.3, is_appropriate=True)
        .order_by("-similarity")
        .values_list("id", "name", "image")[:15]
    )
    return JsonResponse(data={"data": list(queryset)})


def _paginate_via_charity(queryset, page_number: int = 1, page_limit: int = 25) -> dict:
    paginator = Paginator(
        list(
            queryset.select_related("charity").values_list(
                "charity__id", "charity__name", "charity__description"
            )
        ),
        page_limit,
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
    that can take the most inputted items.
    """
    try:
        page_number = int(request.GET.get("page", 1))
        item_ids = [int(x) for x in request.GET.getlist("q")]
    except (TypeError, ValueError):
        raise Http404(_("You must specify the item IDs."))
    # TODO Show which items the org can fulfill for multi-search
    # Not the names since the client already has them. We just need the IDs.
    context = _paginate_via_charity(
        WantedItem.objects.annotate(org_count=Count("charity_id"))
        .filter(item_id__in=item_ids)
        .order_by("-org_count")
        .distinct(),
        page_number,
    )
    return render(request, "pages/home.html", context=context)
