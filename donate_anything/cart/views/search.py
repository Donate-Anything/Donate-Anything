from django.core.paginator import Paginator
from django.db.models.functions import Left
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from donate_anything.item.models import Item, WantedItem


@require_GET
def search_view(request):
    if "q" not in request.GET:
        raise Http404("You must specify an item.")
    try:
        item_id = int(request.GET["q_id"])
    # Handles string, not in query
    except (ValueError, KeyError):
        try:
            item_id = Item.objects.only("id").get(name=request.GET["q"]).id
            return redirect(f"{request.build_absolute_uri()}&q_id={item_id}")
        except (KeyError, Item.DoesNotExist):
            # TODO If user cannot find item, show a page with
            #  other possible options?
            raise Http404
    # TODO Add pic to charities
    paginator = Paginator(
        WantedItem.objects.annotate(
            charity_description=Left("charity__description", 100)
        )
        .select_related("charity")
        .values_list("charity_id", "charity__name", "charity_description",)
        .filter(item_id=item_id)
        .order_by("-id"),
        20,
    )
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "pages/search.html",
        context={
            "page_obj": page_obj,
            "item_id": item_id,
            "item_name": request.GET["q"],
        },
    )
