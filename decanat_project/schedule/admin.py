from django.contrib import admin
from .models import Lesson, ScheduleChange, TimeSlot, AcademicYear


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    ordering = ['-start_date']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'order']
    ordering = ['order', 'start_time']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['day_of_week', 'time_slot', 'subject', 'teacher', 'classroom', 'lesson_type']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['subject', 'teacher', 'group', 'get_day_of_week_display', 'time_slot', 'classroom']
    list_filter = ['day_of_week', 'group', 'teacher', 'lesson_type']
    search_fields = ['subject', 'group', 'classroom', 'teacher__user__last_name']
    ordering = ['group', 'day_of_week', 'time_slot__order']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('subject', 'teacher', 'group', 'lesson_type')
        }),
        ('Расписание', {
            'fields': ('day_of_week', 'time_slot', 'classroom')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher__user', 'time_slot')


@admin.register(ScheduleChange)
class ScheduleChangeAdmin(admin.ModelAdmin):
    list_display = ['original_lesson', 'new_date', 'new_time_slot', 'is_cancelled', 'created_at']
    list_filter = ['is_cancelled', 'new_date', 'created_at']
    search_fields = ['original_lesson__subject', 'original_lesson__group', 'reason']
    date_hierarchy = 'new_date'
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('original_lesson', 'reason', 'is_cancelled')
        }),
        ('Изменения', {
            'fields': ('new_date', 'new_time_slot', 'new_classroom')
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'original_lesson', 
            'original_lesson__teacher__user',
            'new_time_slot'
        )