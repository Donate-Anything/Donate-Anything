from django.db.models import Count
from django.views.generic import ListView

from donate_anything.forum.models import Message, Thread


class ForumView(ListView):
    """Show list of threads with last message
    """

    model = Thread
    paginate_by = 20
    template_name = "forum/landing.html"

    def get_queryset(self):
        """Gets queryset with values: thread id, thread OP username,
        thread created, thread views, last message, last message user,
        last message created, number of replies

        Basically, somewhat copying the django-machina template.
        """
        # Exclude the original post from post count
        return (
            Thread.objects.prefetch_related("message_set")
            .annotate(num_posts=Count("message") - 1)
            .exclude(accepted=True)
            .order_by("-created")
        )


forum_view = ForumView.as_view()


class ThreadView(ListView):
    model = Message
    paginate_by = 30
    template_name = "forum/thread.html"

    def get_queryset(self):
        return Message.objects.order_by("id").filter(thread_id=self.kwargs["thread"])


thread_view = ThreadView.as_view()
