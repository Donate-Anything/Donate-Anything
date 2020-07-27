from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect, requires_csrf_token
from django.views.generic import FormView, UpdateView

from donate_anything.charity.forms import (
    BusinessForm,
    OrganizationForm,
    SuggestedEditForm,
)
from donate_anything.charity.models import (
    AppliedBusinessEdit,
    AppliedOrganizationEdit,
    BusinessApplication,
    OrganizationApplication,
)


class ApplyView(LoginRequiredMixin, FormView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST, user=request.user)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        return super().form_valid(form)


class ApplyOrganizationFormView(ApplyView):
    template_name = "organization/apply/apply_org.html"
    form_class = OrganizationForm

    def get_success_url(self):
        return reverse("charity:applied-organization", kwargs={"pk": self.object.id})


apply_organization_view = ApplyOrganizationFormView.as_view()


class ApplyBusinessFormView(ApplyView):
    template_name = "organization/apply/apply_bus.html"
    form_class = BusinessForm

    def get_success_url(self):
        return reverse("charity:applied-business", kwargs={"pk": self.object.id})


apply_business_view = ApplyBusinessFormView.as_view()


# Editing


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(requires_csrf_token, name="dispatch")
class AppliedBaseUpdateView(LoginRequiredMixin, UpdateView):
    def form_valid(self, form):
        if self.object.applier != self.request.user:
            # This should never happen unless some rando saves a link and goes directly.
            raise HttpResponseForbidden
        form.applier = self.request.user
        self.object = form.save(create_proposed=False)
        return HttpResponse()


class AppliedOrganizationUpdateView(AppliedBaseUpdateView):
    model = OrganizationApplication
    form_class = OrganizationForm

    def get_object(self, queryset=None):
        return OrganizationApplication.objects.get(id=self.kwargs["pk"])


applied_organization_update_view = AppliedOrganizationUpdateView.as_view()


class AppliedBusinessUpdateView(AppliedBaseUpdateView):
    model = BusinessApplication
    form_class = BusinessForm

    def get_object(self, queryset=None):
        return BusinessApplication.objects.get(id=self.kwargs["pk"])


applied_business_update_view = AppliedBusinessUpdateView.as_view()


class SuggestEditView(LoginRequiredMixin, FormView):
    form_class = SuggestedEditForm
    model = None
    parent_model = None

    def form_valid(self, form):
        pk = form.cleaned_data["id"]
        create = form.cleaned_data["create"]
        if create.lower() == "true":
            if self.parent_model.objects.filter(id=pk).exists():
                obj = self.model.objects.create(
                    user=self.request.user,
                    edit=form.cleaned_data["edit"],
                    proposed_entity_id=pk,
                )
                return JsonResponse(
                    {"id": obj.id, "username": self.request.user.get_username()}
                )
            else:
                return HttpResponseBadRequest(_("Application doesn't exist."))
        else:
            try:
                obj = self.model.objects.get(id=pk)
            except self.model.DoesNotExist:
                return HttpResponseForbidden(_("Suggestion does not exist."))
            if obj.user != self.request.user:
                return HttpResponseForbidden(_("You may not edit this suggestion."))
            obj.edit = form.cleaned_data["edit"]
            obj.save(update_fields=["edit"])
        return HttpResponse()

    def form_invalid(self, form):
        return HttpResponseBadRequest(_("Must fill in all fields."))


class SuggestEditAppliedOrgView(SuggestEditView):
    model = AppliedOrganizationEdit
    parent_model = OrganizationApplication


suggest_edit_org_form_view = SuggestEditAppliedOrgView.as_view()


class SuggestEditAppliedBusView(SuggestEditView):
    model = AppliedBusinessEdit
    parent_model = BusinessApplication


suggest_edit_bus_form_view = SuggestEditAppliedBusView.as_view()
