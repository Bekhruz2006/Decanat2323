from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TeacherGroupAccess, News, Contact


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'middle_name', 'phone', 'photo', 'birth_date', 'address')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'first_name', 'last_name', 'middle_name', 'email')
        }),
    )


@admin.register(TeacherGroupAccess)
class TeacherGroupAccessAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'group', 'subject', 'can_edit']
    list_filter = ['group', 'can_edit']
    search_fields = ['teacher__username', 'teacher__last_name', 'group', 'subject']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher":
            kwargs["queryset"] = User.objects.filter(role='teacher')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_important', 'created_at']
    list_filter = ['is_important', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['title', 'phone', 'email', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'phone', 'email']
    ordering = ['order', 'title']