from django import forms

from donate_anything.charity.forms import MDWidget
from donate_anything.forum.models import Message


class ForumForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("message",)
        widgets = {"message": MDWidget()}

    def __init__(self, *args, **kwargs):
        # User instance
        self.user = kwargs.pop("user", None)
        # Thread id
        self.thread: int = kwargs.pop("thread", None)
        super(ForumForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ForumForm, self).save(commit=False)
        instance.user = self.user
        instance.thread_id = self.thread
        if commit:
            instance.save()
        return instance
