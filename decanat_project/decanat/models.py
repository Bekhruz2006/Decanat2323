from django.db import models
from django.conf import settings


class Teacher(models.Model):
    """Модель преподавателя"""
    POSITIONS = [
        ('professor', 'Профессор'),
        ('docent', 'Доцент'),
        ('senior_lecturer', 'Старший преподаватель'),
        ('assistant', 'Ассистент'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name='teacher_profile'
    )
    position = models.CharField('Должность', max_length=50, choices=POSITIONS)
    department = models.CharField('Кафедра', max_length=200)
    
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_position_display()}"


class Student(models.Model):
    """Модель студента"""
    FINANCING_TYPES = [
        ('budget', 'Бюджет'),
        ('contract', 'Договор'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name='student_profile'
    )
    group = models.CharField('Группа', max_length=50)
    record_book_number = models.CharField('Номер зачётки', max_length=20, unique=True)
    financing_type = models.CharField('Тип финансирования', max_length=20, choices=FINANCING_TYPES)
    
    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['group', 'user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group} ({self.record_book_number})"


class Curriculum(models.Model):
    """Модель учебного плана"""
    name = models.CharField('Название', max_length=200)
    specialty = models.CharField('Специальность', max_length=200)
    semester = models.PositiveIntegerField('Семестр')
    group = models.CharField('Группа', max_length=50, blank=True)
    curriculum_file = models.FileField('Файл учебного плана', upload_to='curriculums/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Учебный план'
        verbose_name_plural = 'Учебные планы'
        ordering = ['specialty', 'semester']
    
    def __str__(self):
        return f"{self.name} - {self.specialty} (Семестр {self.semester})"