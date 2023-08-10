from django.utils.html import format_html
from django.contrib import admin
from .models import *

@admin.register(user_registration)
class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user_id','display_image' , 'first_name', 'last_name', 'email_address', 'mobile_number', 'aadhaar_number', 'user_type', 'status')
    list_filter = ('user_type', 'aadhaar_number', 'status')
    search_fields = ('first_name', 'last_name', 'email_address', 'mobile_number','aadhaar_number')

    def display_image(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" style="vertical-align: middle; width: 50px; height: 50px; border-radius: 50%;"/>', obj.profile_photo.url)
        else:
            return '-'
    display_image.allow_tags = True
    display_image.short_description = 'Profile Picture'

    def user_id(self, obj):
        return format_html('#{}', obj.unique_id)
    
@admin.register(messages_index)
class MessagesIndexAdmin(admin.ModelAdmin):
    list_display = ['unique_id', 'recipient_user', 'sender_user', 'date_added']
    search_fields = ['recipient_user__first_name', 'sender_user__first_name']

@admin.register(messages_contain)
class MessagesContainAdmin(admin.ModelAdmin):
    list_display = ['unique_id', 'msg_index', 'participant_user', 'messages_text', 'message_type', 'date_added']
    list_filter = ['message_type']
    search_fields = ['msg_index__recipient_user__first_name', 'participant_user__first_name', 'messages_text']


@admin.register(elections)
class ElectionsAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'election_start_date_time', 'election_end_date_time', 'status', 'date_added')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)

@admin.register(election_parties)
class ElectionPartiesAdmin(admin.ModelAdmin):
    list_display = ('party_name', 'elections', 'tag_line', 'date_added')
    search_fields = ('party_name', 'elections__title', 'tag_line')
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)


@admin.register(election_position)
class ElectionPositionAdmin(admin.ModelAdmin):
    list_display = ('postion_name', 'elections', 'tag_line', 'date_added')
    search_fields = ('postion_name', 'elections__title', 'tag_line')
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)


@admin.register(election_candidates)
class ElectionCandidatesAdmin(admin.ModelAdmin):
    list_display = ('candidates', 'elections', 'party', 'position', 'symbol_name', 'status', 'date_added')
    list_filter = ('status', 'party', 'position', 'elections',)
    search_fields = ('candidates__username', 'elections__title', 'party__party_name', 'position__postion_name', 'symbol_name')
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)


@admin.register(election_votes)
class ElectionVotesAdmin(admin.ModelAdmin):
    list_display = ('elections', 'position', 'candidates', 'voters', 'vote', 'date_added')
    list_filter = ('elections', 'position', 'candidates',)
    search_fields = ('elections__title', 'position__postion_name', 'candidates__candidates__username', 'voters__username')
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)    