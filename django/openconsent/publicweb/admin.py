from django.contrib import admin
from models import Decision, Group, Concern

class ConcernInline(admin.TabularInline):
    model = Concern
    extra = 1

class DecisionAdmin(admin.ModelAdmin):
    list_display = ('short_name','decided_date','effective_date','review_date','expiry_date','budget','people','group')
    search_fields = ('short_name',)
    list_filter = ('decided_date','effective_date','review_date','expiry_date',)
    inlines = (ConcernInline,)

class ConcernAdmin(admin.ModelAdmin):
    list_display = ('short_name','description')
        
admin.site.register(Group)
admin.site.register(Concern,ConcernAdmin)
admin.site.register(Decision,DecisionAdmin)