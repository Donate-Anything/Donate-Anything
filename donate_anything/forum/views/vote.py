from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseForbidden

from donate_anything.forum.models.forum import Thread
from donate_anything.forum.models.vote import UserVote


@login_required
def vote(request, thread_id: int, vote_dir: int):
    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        raise Http404
    if not thread.is_votable_thread or thread.accepted:
        return HttpResponseForbidden()
    UserVote.objects.update_or_create(
        thread_id=thread_id,
        user=request.user,
        defaults={
            "thread_id": thread_id,
            "user": request.user,
            "direction": (True if vote_dir == 1 else False),
        },
    )
    return HttpResponse()
