from django.contrib import admin
from .models import DAO, Proposal, Vote

admin.site.register(DAO)
#admin.site.register(DAOMember)
admin.site.register(Proposal)
admin.site.register(Vote)