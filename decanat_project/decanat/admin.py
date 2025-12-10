from django.contrib import admin
from .models import Student, Teacher, Curriculum


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['get_last_name', 'get_first_name', 'group', 'record_book_number', 'financing_type']
    list_filter = ['group', 'financing_type']
    search_fields = ['user__last_name', 'user__first_name', 'record_book_number', 'group']
    ordering = ['group', 'user__last_name']
    
    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Фамилия'
    get_last_name.admin_order_field = 'user__last_name'
    
    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Имя'
    get_first_name.admin_order_field = 'user__first_name'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['get_last_name', 'get_first_name', 'position', 'department']
    list_filter = ['position', 'department']
    search_fields = ['user__last_name', 'user__first_name', 'department']
    ordering = ['user__last_name']
    
    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Фамилия'
    get_last_name.admin_order_field = 'user__last_name'
    
    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Имя'
    get_first_name.admin_order_field = 'user__first_name'


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'semester', 'group', 'created_at']
    list_filter = ['semester', 'specialty', 'group']
    search_fields = ['name', 'specialty', 'group']
    ordering = ['specialty', 'semester']
    readonly_fields = ['created_at', 'updated_at']