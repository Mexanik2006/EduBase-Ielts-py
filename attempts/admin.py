from django.contrib import admin
from .models import Attempt, Review, AttemptAudio

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'group', 'status', 'total_score', 'created_at']
    list_filter = ['status', 'exam__section_type', 'created_at']
    search_fields = ['student__username', 'exam__title', 'group__name']
    readonly_fields = ['created_at', 'started_at']

# @admin.register(AttemptAudio)
# class AttemptAudioAdmin(admin.ModelAdmin):
#     list_display = ['attempt', 'part_id', 'audio_file', 'created_at']
#     list_filter = ['created_at', 'part_id']
#     search_fields = ['attempt__student__username', 'attempt__exam__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'mentor', 'overall_score', 'reviewed_at']
    list_filter = ['reviewed_at', 'overall_score']
    search_fields = ['attempt__student__username', 'attempt__exam__title', 'mentor__username']
