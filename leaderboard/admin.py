from django.contrib import admin
from .models import CrowdFundingChallenge, Transaction, Competition, Challenge

@admin.register(CrowdFundingChallenge)
class CrowdFundingChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'target_amount', 'current_amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'created_by__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'user', 'amount', 'transaction_date')
    list_filter = ('transaction_date', 'challenge')
    search_fields = ('user__username', 'challenge__title')

admin.site.register(Competition)
admin.site.register(Challenge)