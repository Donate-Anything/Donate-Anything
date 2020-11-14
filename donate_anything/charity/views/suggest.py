from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView

from donate_anything.charity.forms import ExistingSuggestEditForm
from donate_anything.users.models.charity import VerifiedAccount


@method_decorator(csrf_protect, name="dispatch")
class SuggestActiveEditView(LoginRequiredMixin, FormView):
    form_class = ExistingSuggestEditForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.is_verified = False

    def get_success_url(self):
        return reverse("forum:home")

    def post(self, request, *args, **kwargs):
        self.is_verified = VerifiedAccount.objects.filter(
            user=self.request.user, charity=self.kwargs["pk"], accepted=True
        ).exists()
        form = self.get_form_class()(
            request.POST,
            user=request.user,
            entity=self.kwargs["pk"],
            is_verified=self.is_verified,
        )
        if form.is_valid() and request.user.is_authenticated:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        if self.is_verified:
            # form.entity is already set to Charity object
            update_fields = []
            for field in ("description", "how_to_donate", "link", "logo"):
                try:
                    if form.cleaned_data[field]:
                        setattr(form.entity, field, form.cleaned_data[field])
                        update_fields.append(field)
                except KeyError:
                    continue
            form.entity.save(update_fields=update_fields)
            messages.add_message(
                self.request,
                messages.INFO,
                _("Successfully updated."),
            )
            return HttpResponseRedirect(
                reverse("charity:organization", kwargs={"pk": form.entity.id})
            )
        else:
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
