from django.contrib import admin
from dashboard.models import Verify, Profile, Notification, Transaction, Contribute, Loan, Mentorship
from dashboard.models import Success_Story, Message, Blog

admin.site.register(Verify)
admin.site.register(Profile)
admin.site.register(Notification)
admin.site.register(Transaction)
admin.site.register(Contribute)
admin.site.register(Loan)
admin.site.register(Mentorship)
admin.site.register(Success_Story)
admin.site.register(Message)
admin.site.register(Blog)