from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, requires_csrf_token
from django.views.generic import FormView, UpdateView

from donate_anything.charity.forms import BusinessForm, OrganizationForm
from donate_anything.charity.models import BusinessApplication, OrganizationApplication


class ApplyOrganizationFormView(LoginRequiredMixin, FormView):
    template_name = "organization/apply/apply_org.html"
    form_class = OrganizationForm

    def __init__(self, *args, **kwargs):
        super(ApplyOrganizationFormView, self).__init__(*args, **kwargs)
        self.object = None

    def get_success_url(self):
        return reverse("charity:applied-organization", kwargs={"pk": self.object.id})

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


apply_organization_view = ApplyOrganizationFormView.as_view()


class ApplyBusinessFormView(LoginRequiredMixin, FormView):
    template_name = "organization/apply/apply_bus.html"
    form_class = BusinessForm

    def __init__(self, *args, **kwargs):
        super(ApplyBusinessFormView, self).__init__(*args, **kwargs)
        self.object = None

    def get_success_url(self):
        return reverse("charity:applied-business", kwargs={"pk": self.object.id})

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
