from django.contrib import admin
from .models import Attendance, Grade, StudentProfile


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'week_number']
    list_filter = ['status', 'date', 'subject', 'week_number']
    search_fields = ['student__user__last_name', 'student__user__first_name', 'subject']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'get_grade_display', 'exam_type', 'date', 'week_number']
    list_filter = ['is_nb', 'exam_type', 'date', 'week_number']
    search_fields = ['student__user__last_name', 'student__user__first_name', 'subject']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['can_edit']
    
    def get_grade_display(self, obj):
        if obj.is_nb:
            return 'НБ'
        return obj.score
    get_grade_display.short_description = 'Оценка'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'teacher__user')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student', 'get_average_score', 'get_total_attendance', 'total_nb', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['student__user__last_name', 'student__user__first_name', 'student__record_book_number']
    readonly_fields = ['updated_at']
    ordering = ['-average_score']
    
    actions = ['recalculate_statistics']
    
    def get_average_score(self, obj):
        return f"{obj.average_score:.2f}"
    get_average_score.short_description = 'Средний балл'
    get_average_score.admin_order_field = 'average_score'
    
    def get_total_attendance(self, obj):
        return f"{obj.total_attendance}/{obj.total_lessons}"
    get_total_attendance.short_description = 'Посещаемость'
    
    def recalculate_statistics(self, request, queryset):
        """Пересчитать статистику для выбранных профилей"""
        for profile in queryset:
            profile.calculate_average_score()
            profile.calculate_attendance()
            profile.calculate_nb_count()
        self.message_user(request, f"Статистика пересчитана для {queryset.count()} профилей")
    
    recalculate_statistics.short_description = "Пересчитать статистику"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user')