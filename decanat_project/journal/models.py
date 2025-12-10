from django.db import models
from django.utils import timezone
from decanat.models import Student
from datetime import datetime, timedelta


class Attendance(models.Model):
    """Модель посещаемости"""
    ATTENDANCE_STATUS = [
        ('present', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('late', 'Опоздал'),
        ('excused', 'Уважительная причина'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент', related_name='attendances')
    date = models.DateField('Дата')
    subject = models.CharField('Предмет', max_length=200)
    status = models.CharField('Статус присутствия', max_length=20, choices=ATTENDANCE_STATUS)
    notes = models.TextField('Примечания', blank=True)
    week_number = models.IntegerField('Номер недели', default=1)
    
    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        ordering = ['-date', 'student']
        unique_together = ['student', 'date', 'subject']
    
    def __str__(self):
        return f"{self.student.user.last_name} - {self.subject} ({self.date}) - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Автоматически вычисляем номер недели
        if not self.week_number:
            self.week_number = self.date.isocalendar()[1]
        super().save(*args, **kwargs)


class Grade(models.Model):
    """Модель оценки с балльной системой"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент', related_name='grades')
    subject = models.CharField('Предмет', max_length=200)
    score = models.IntegerField('Баллы', null=True, blank=True)  # 1-12 баллов
    is_nb = models.BooleanField('НБ (не был)', default=False)
    date = models.DateField('Дата')
    week_number = models.IntegerField('Номер недели', default=1)
    exam_type = models.CharField('Тип контроля', max_length=50, default='текущий')
    can_edit = models.BooleanField('Можно редактировать', default=True)
    teacher = models.ForeignKey(
        'decanat.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Преподаватель'
    )
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['-date', 'student']
    
    def __str__(self):
        if self.is_nb:
            return f"{self.student.user.last_name} - {self.subject}: НБ ({self.date})"
        return f"{self.student.user.last_name} - {self.subject}: {self.score} ({self.date})"
    
    def save(self, *args, **kwargs):
        # Автоматически вычисляем номер недели
        if not self.week_number:
            self.week_number = self.date.isocalendar()[1]
        
        # Блокируем редактирование после окончания дня
        if self.pk:
            today = timezone.now().date()
            if self.date < today:
                self.can_edit = False
        
        super().save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_nb and self.score:
            raise ValidationError('Нельзя одновременно указать баллы и отметку НБ')
        if not self.is_nb and self.score is None:
            raise ValidationError('Укажите баллы или отметьте НБ')
        if self.score and (self.score < 1 or self.score > 12):
            raise ValidationError('Баллы должны быть от 1 до 12')


class StudentProfile(models.Model):
    """Модель профиля студента с полной сводкой"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, verbose_name='Студент', related_name='profile')
    average_score = models.DecimalField('Средний балл', max_digits=4, decimal_places=2, default=0.00)
    total_attendance = models.IntegerField('Всего посещено', default=0)
    total_nb = models.IntegerField('Всего НБ', default=0)
    total_lessons = models.IntegerField('Всего занятий', default=0)
    debts = models.TextField('Задолженности', blank=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'
    
    def __str__(self):
        return f"Профиль: {self.student.user.get_full_name()}"
    
    def calculate_average_score(self):
        """Рассчитать средний балл"""
        grades = self.student.grades.filter(is_nb=False, score__isnull=False)
        if grades.exists():
            total = sum(g.score for g in grades)
            self.average_score = total / grades.count()
        else:
            self.average_score = 0.00
        self.save()
    
    def calculate_attendance(self):
        """Рассчитать посещаемость"""
        attendances = self.student.attendances.all()
        self.total_lessons = attendances.count()
        self.total_attendance = attendances.filter(status__in=['present', 'late']).count()
        self.save()
    
    def calculate_nb_count(self):
        """Подсчитать количество НБ"""
        self.total_nb = self.student.grades.filter(is_nb=True).count()
        self.save()