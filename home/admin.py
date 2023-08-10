from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email_address', 'date_added', 'date_updated')
    list_filter = ('date_added', 'date_updated')
    search_fields = ('full_name', 'email_address', 'message')
    date_hierarchy = 'date_added'
