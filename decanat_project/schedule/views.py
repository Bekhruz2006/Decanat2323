from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Lesson, ScheduleChange
from .forms import ScheduleChangeForm


class ScheduleView(ListView):
    model = Lesson
    template_name = 'schedule/schedule_list.html'
    context_object_name = 'lessons'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('teacher__user', 'time_slot')
        group = self.request.GET.get('group')
        day = self.request.GET.get('day')
        
        if group:
            queryset = queryset.filter(group=group)
        
        if day:
            queryset = queryset.filter(day_of_week=day)
        
        return queryset.order_by('day_of_week', 'time_slot__order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from decanat.models import Student
        
        # Группируем занятия по дням недели
        lessons_by_day = {}
        for lesson in context['lessons']:
            day = lesson.get_day_of_week_display()
            if day not in lessons_by_day:
                lessons_by_day[day] = []
            lessons_by_day[day].append(lesson)
        
        context['lessons_by_day'] = lessons_by_day
        context['groups'] = Student.objects.values_list('group', flat=True).distinct().order_by('group')
        context['days_of_week'] = Lesson.DAYS_OF_WEEK
        context['current_group'] = self.request.GET.get('group', '')
        context['current_day'] = self.request.GET.get('day', '')
        
        # Получаем последние изменения расписания
        context['recent_changes'] = ScheduleChange.objects.select_related(
            'original_lesson', 'original_lesson__teacher__user', 'new_time_slot'
        ).order_by('-created_at')[:10]
        
        return context


class ScheduleChangeCreateView(CreateView):
    model = ScheduleChange
    form_class = ScheduleChangeForm
    template_name = 'schedule/schedule_change_form.html'
    success_url = reverse_lazy('schedule:schedule_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Изменение расписания успешно создано!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons'] = Lesson.objects.select_related('teacher__user', 'time_slot').order_by('day_of_week', 'time_slot__order')
        return context