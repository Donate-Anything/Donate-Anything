from django.contrib import admin

from .models import Message, Thread, UserVote


admin.site.register(Thread)
admin.site.register(Message)
admin.site.register(UserVote)
