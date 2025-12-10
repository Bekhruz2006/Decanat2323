from django.db import models
from decanat.models import Teacher


class AcademicYear(models.Model):
    """Учебный год с настройкой начала отсчёта недель"""
    name = models.CharField('Название', max_length=50)  # например "2024/2025"
    start_date = models.DateField('Дата начала учебного года')
    end_date = models.DateField('Дата окончания учебного года')
    is_active = models.BooleanField('Активный', default=True)
    
    class Meta:
        verbose_name = 'Учебный год'
        verbose_name_plural = 'Учебные годы'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def get_week_number(self, date):
        """Получить номер недели от начала учебного года"""
        if date < self.start_date:
            return 0
        delta = date - self.start_date
        return (delta.days // 7) + 1


class TimeSlot(models.Model):
    """Временной слот для занятий"""
    name = models.CharField('Название', max_length=50)  # например "1 пара"
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания')
    order = models.IntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Временной слот'
        verbose_name_plural = 'Временные слоты'
        ordering = ['order', 'start_time']
    
    def __str__(self):
        return f"{self.name}: {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"


class Lesson(models.Model):
    """Модель занятия с недельной системой"""
    DAYS_OF_WEEK = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
    ]
    
    subject = models.CharField('Предмет', max_length=200)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Преподаватель', related_name='lessons')
    group = models.CharField('Группа', max_length=50)
    classroom = models.CharField('Аудитория', max_length=50)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, verbose_name='Временной слот', related_name='lessons')
    day_of_week = models.IntegerField('День недели', choices=DAYS_OF_WEEK)
    lesson_type = models.CharField('Тип занятия', max_length=50, default='лекция')
    
    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['day_of_week', 'time_slot__order']
        unique_together = ['group', 'day_of_week', 'time_slot']
    
    def __str__(self):
        return f"{self.subject} - {self.group} ({self.get_day_of_week_display()}, {self.time_slot})"


class ScheduleChange(models.Model):
    """Модель изменения расписания"""
    original_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='Оригинальное занятие', related_name='changes')
    new_date = models.DateField('Новая дата', null=True, blank=True)
    new_time_slot = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Новый временной слот')
    new_classroom = models.CharField('Новая аудитория', max_length=50, blank=True)
    reason = models.TextField('Причина изменения')
    is_cancelled = models.BooleanField('Занятие отменено', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Изменение расписания'
        verbose_name_plural = 'Изменения расписания'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.is_cancelled:
            return f"Отмена: {self.original_lesson.subject} - {self.original_lesson.group}"
        return f"Изменение: {self.original_lesson.subject} - {self.new_date or 'без изменения даты'}"




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