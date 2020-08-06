from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView

from donate_anything.charity.forms import ExistingSuggestEditForm


@method_decorator(csrf_protect, name="dispatch")
class SuggestActiveEditView(LoginRequiredMixin, FormView):
    form_class = ExistingSuggestEditForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_success_url(self):
        return reverse("forum:home")

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(
            request.POST, user=request.user, entity=self.kwargs["pk"]
        )
        if form.is_valid() and request.user.is_authenticated:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.add_message(
            self.request,
            messages.INFO,
            _("Successfully posted edit. Wait for community review."),
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            _(
                "You must change at least one field to suggest an edit with a edit/commit message."
            ),
        )
        return HttpResponseRedirect(
            reverse("charity:organization", kwargs={"pk": self.kwargs["pk"]})
        )


suggest_active_org_edit_view = SuggestActiveEditView.as_view()
