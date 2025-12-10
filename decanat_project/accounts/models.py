from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя"""
    ROLE_CHOICES = [
        ('decanat', 'Деканат'),
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    ]
    
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='student')
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    photo = models.ImageField('Фото профиля', upload_to='profiles/', blank=True, null=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    address = models.TextField('Адрес', blank=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            ('view_all_students', 'Может просматривать всех студентов'),
            ('edit_all_students', 'Может редактировать всех студентов'),
            ('view_all_grades', 'Может просматривать все оценки'),
            ('edit_grades', 'Может редактировать оценки'),
            ('view_all_attendance', 'Может просматривать всю посещаемость'),
            ('manage_schedule', 'Может управлять расписанием'),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        full_name = f"{self.last_name} {self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        return full_name


class TeacherGroupAccess(models.Model):
    """Доступ преподавателя к группам"""
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'teacher'},
        verbose_name='Преподаватель',
        related_name='group_access'
    )
    group = models.CharField('Группа', max_length=50)
    subject = models.CharField('Предмет', max_length=200)
    can_edit = models.BooleanField('Может редактировать', default=True)
    
    class Meta:
        verbose_name = 'Доступ преподавателя'
        verbose_name_plural = 'Доступы преподавателей'
        unique_together = ['teacher', 'group', 'subject']
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.group} ({self.subject})"


class News(models.Model):
    """Новости и объявления"""
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_important = models.BooleanField('Важное', default=False)
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


# Добавьте этот класс в конец файла accounts/models.py

class Contact(models.Model):
    """Контактная информация деканата"""
    title = models.CharField('Заголовок', max_length=200)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    telegram = models.CharField('Telegram', max_length=100, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=50, blank=True)
    facebook = models.URLField('Facebook', blank=True)
    address = models.TextField('Адрес', blank=True)
    working_hours = models.TextField('Часы работы', blank=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активный', default=True)
    
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title