from django.contrib import admin
from .models import Group, GroupStudent

class GroupStudentInline(admin.TabularInline):
    model = GroupStudent
    extra = 0

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'mentor', 'student_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'mentor__username', 'mentor__first_name', 'mentor__last_name']
    inlines = [GroupStudentInline]
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'

@admin.register(GroupStudent)
class GroupStudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'joined_at']
    list_filter = ['group', 'joined_at']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'group__name']
