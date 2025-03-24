from django.contrib import admin
from .models import InvestmentOpportunity, MemberInvestmentRequest, MentorshipProgram

admin.site.register(InvestmentOpportunity)
admin.site.register(MemberInvestmentRequest)
admin.site.register(MentorshipProgram)