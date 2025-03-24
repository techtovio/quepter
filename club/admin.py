from django.contrib import admin

# Register your models here.
from .models import Club, ClubBroadcast, ClubMembership, ClubContribution

admin.site.register(Club)
admin.site.register(ClubMembership)
admin.site.register(ClubBroadcast)
admin.site.register(ClubContribution)