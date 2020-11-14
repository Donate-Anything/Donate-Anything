from string import digits
from typing import Iterable

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect, requires_csrf_token
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView

from donate_anything.charity.models.charity import Charity
from donate_anything.item.forms import ModifyItemsForm
from donate_anything.item.models.category import CATEGORY_TYPES, Category
from donate_anything.item.models.item import Item, ProposedItem, WantedItem
from donate_anything.item.utils.base_converter import (
    b64_to_wanted_item,
    item_encode_b64,
)
from donate_anything.users.models.charity import VerifiedAccount


def search_item_autocomplete(request):
    """Simple autocomplete for all existing items."""
    # TODO Migrate to elasticsearch once there's enough items
    # TODO Use websockets instead since elasticsearch-dsl supports asyncio
    query = request.GET.get("q", None)
    if query is None:
        raise Http404(_("You must specify a query"))
    queryset = (
        Item.objects.defer("is_appropriate")
        .annotate(similarity=TrigramSimilarity("name", query))
        .filter(name__icontains=str(query), is_appropriate=True)
        .values_list("id", "name", "image")
        .order_by("-similarity")[:15]
    )
    data = {"data": list(queryset)}
    try:
        # Give the item ID with condition appended
        condition = int(request.GET.get("condition"))
        for item in data["data"]:
            item[0] = item_encode_b64(item[0], condition)
    except (KeyError, ValueError, TypeError):
        pass
    return JsonResponse(data=data)


def item_children(request, item_id):
    """Given an item, find all its child items, and their child items etc.
    Doesn't include parent since we assume it's already known.
    Used mostly for inputting items.
    """
    if not request.user.is_authenticated:
        raise Http404
    children_ids = []
    children_names = []
    new_children = [
        (x.id, x.name)
        for x in Item.objects.only("id", "name").filter(
            parent_id=item_id, is_appropriate=True
        )
    ]
    while new_children:
        try:
            current_id = new_children[0][0]
        except IndexError:
            break
        if current_id in children_ids or current_id == item_id:
            new_children.pop(0)
            continue
        new_children += [
            (x.id, x.name)
            for x in Item.objects.only("id", "name").filter(
                parent_id=current_id, is_appropriate=True
            )
        ]
        children_ids.append(current_id)
        children_names.append(new_children[0][1])
        new_children.pop(0)

    return JsonResponse(data={"data": tuple(zip(children_ids, children_names))})


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


def search_item(request, pk: str):
    """Shows charities that can fulfill the selected items
    within the current page.
    """
    try:
        item_id, condition = b64_to_wanted_item(pk)
    except ValueError:
        return HttpResponseBadRequest(_("You must specify the condition and item ID."))
    except AssertionError:
        return HttpResponseBadRequest(_("The id cannot be a single digit."))
    return JsonResponse(
        _paginate_via_charity(
            WantedItem.objects.filter(item_id=item_id, condition__lte=condition),
            request.GET.get("page"),
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
        queries = request.GET.getlist("q")
        assert not any(x in digits for x in queries)
        item_ids, conditions = zip(*set(b64_to_wanted_item(x) for x in queries))
    except (TypeError, ValueError):
        raise Http404(_("You must specify the item IDs."))
    except AssertionError:
        return HttpResponseBadRequest(_("An item cannot just be a number."))

    # Load all charities that can fulfill any item asked for.
    # FIXME Multi-search has to practically load an entire database
    #  because organizations can have thousands of WantedItems.
    #  There is a fix: Trigram and marking items as duplicates.
    #  Follow GH #3 https://github.com/Donate-Anything/Donate-Anything/issues/3
    # Or you can just find a better query :P
    queryset = WantedItem.objects.filter(item_id__in=item_ids).values_list(
        "charity_id", "item_id", "condition"
    )
    charity_fulfillment: dict = {}
    for charity_id, item_id, item_condition in queryset:
        try:
            i = item_ids.index(item_id)
            try:
                if conditions[i] >= item_condition:
                    charity_fulfillment[charity_id].append(item_id)
            except KeyError:
                if conditions[i] >= item_condition:
                    try:
                        charity_fulfillment[charity_id] = [item_id]
                    except KeyError:
                        break
            except IndexError:
                break
        except ValueError:
            break
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
        # The array context is currently the item IDs. The HTML strips the last
        # two elements, name + description, and checks the length to find
        # the number of items the charity can fulfill.
        charity_fulfillment[c_id].extend([name, description[:150]])

    context = {
        "data": charity_fulfillment,
        "page_obj": page_obj,
    }

    return render(request, "organization/multiple_orgs.html", context=context)


def _can_delete_wanted_items(request, charity_id: int) -> bool:
    try:
        if request.user.is_anonymous:
            return False
        if not VerifiedAccount.objects.filter(
            user=request.user, charity_id=charity_id, accepted=True
        ).exists():
            if not request.user.is_staff:
                return False
        return True
    except AttributeError:
        return False


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
    can_delete = _can_delete_wanted_items(request, charity_id)
    _wanted_item_args = ["item__name", "condition"]
    if can_delete:
        _wanted_item_args.append("id")
    if Charity.objects.filter(id=charity_id).exists():
        # Apparently using select/prefetch_related("item") makes it 10x slower
        qs = (
            WantedItem.objects.filter(charity_id=charity_id, item__is_appropriate=True)
            .order_by("item__name")
            .values_list(*_wanted_item_args)
        )
    else:
        raise Http404
    paginator = Paginator(qs, 50)
    try:
        num = paginator.validate_number(request.GET.get("page", 1))
    except (EmptyPage, PageNotAnInteger):
        raise Http404
    page_obj = paginator.page(num)
    return JsonResponse(
        {"data": list(page_obj.object_list), "has_next": page_obj.has_next()}
    )


def list_org_items_view(request, entity_id):
    """View that renders the initial items list"""
    obj = get_object_or_404(Charity, id=entity_id)
    return render(
        request,
        "organization/list_item.html",
        {
            "id": entity_id,
            "name": obj.name,
            "can_delete": _can_delete_wanted_items(request, entity_id),
        },
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
    # Sort by id so that the condition array is also sorted
    conditions = [
        proposed_item_obj.item_condition[proposed_item_obj.item.index(x.id)] for x in qs
    ]
    return JsonResponse(
        {
            "data": [(x.id, x.name) for x in qs],
            "condition": conditions,
            "has_next": page_obj.has_next(),
        }
    )


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


@method_decorator(requires_csrf_token, name="dispatch")
class InitialProposedItemTemplate(LoginRequiredMixin, TemplateView):
    template_name = "organization/suggest/initial_propose_item.html"


initial_proposed_item_template = InitialProposedItemTemplate.as_view()


# Only need requires_csrf_token when it's a form in template view
@method_decorator(csrf_protect, name="dispatch")
class ProposedItemFormView(LoginRequiredMixin, FormView):
    """Form view for proposed item fill out."""

    form_class = ModifyItemsForm

    def form_valid(self, form):
        # Prepare data:
        updated = {
            "item": form.cleaned_data["item"],
            "item_condition": form.cleaned_data["item_condition"],
            "names": form.cleaned_data["names"],
            "names_condition": form.cleaned_data["names_condition"],
        }

        # Determine if create or update
        if form.cleaned_data["id"] is None:
            # User is redirected to forum
            ProposedItem.objects.create(
                user=self.request.user, entity_id=form.cleaned_data["entity"], **updated
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
            ).update(**updated)
        return HttpResponse()

    def form_invalid(self, form):
        return JsonResponse({"errors": form.errors}, status=400)


proposed_item_form_view = ProposedItemFormView.as_view()


@require_POST
def delete_items(request, wanted_item_id):
    """Only VerifiedAccounts can delete items from list_item.html"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden
    obj = get_object_or_404(WantedItem.objects.only("charity_id"), pk=wanted_item_id)
    if not _can_delete_wanted_items(request, obj.charity_id):
        return HttpResponseForbidden
    obj.delete()
    return HttpResponse()
