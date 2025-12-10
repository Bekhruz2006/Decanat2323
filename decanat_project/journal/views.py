from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from .models import Attendance, Grade, StudentProfile
from .forms import GradeForm, WeekFilterForm
from .utils import get_academic_week_number, get_current_academic_year
from decanat.models import Student


class GradesByWeekView(LoginRequiredMixin, ListView):
    """Просмотр оценок по неделям"""
    model = Grade
    template_name = 'journal/grades_by_week.html'
    context_object_name = 'grades'
    
    def get_queryset(self):
        queryset = Grade.objects.select_related('student__user', 'teacher__user')
        
        week = self.request.GET.get('week')
        year = self.request.GET.get('year')
        group = self.request.GET.get('group')
        subject = self.request.GET.get('subject')
        
        if week and year:
            queryset = queryset.filter(week_number=week, date__year=year)
        
        if group:
            queryset = queryset.filter(student__group=group)
        
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        
        # Ограничения по роли
        if self.request.user.role == 'student':
            try:
                student = Student.objects.get(user=self.request.user)
                queryset = queryset.filter(student=student)
            except Student.DoesNotExist:
                queryset = queryset.none()
        
        elif self.request.user.role == 'teacher':
            from accounts.models import TeacherGroupAccess
            teacher_groups = TeacherGroupAccess.objects.filter(
                teacher=self.request.user
            ).values_list('group', flat=True)
            
            if teacher_groups:
                queryset = queryset.filter(student__group__in=teacher_groups)
        
        return queryset.order_by('-date', 'student__user__last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = WeekFilterForm(self.request.GET or None)
        context['groups'] = Student.objects.values_list('group', flat=True).distinct().order_by('group')
        context['subjects'] = Grade.objects.values_list('subject', flat=True).distinct()
        
        # Используем правильный подсчёт недель
        week = self.request.GET.get('week')
        if not week:
            week = get_academic_week_number()
        
        context['current_week'] = int(week)
        context['current_year'] = self.request.GET.get('year', datetime.now().year)
        context['academic_year'] = get_current_academic_year()
        return context


class GradeCreateView(LoginRequiredMixin, CreateView):
    """Выставление оценок преподавателем"""
    model = Grade
    form_class = GradeForm
    template_name = 'journal/grade_form.html'
    success_url = reverse_lazy('journal:grades_by_week')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        grade = form.save(commit=False)
        
        # Привязываем преподавателя
        if self.request.user.role == 'teacher':
            from decanat.models import Teacher
            try:
                teacher = Teacher.objects.get(user=self.request.user)
                grade.teacher = teacher
            except Teacher.DoesNotExist:
                pass
        
        response = super().form_valid(form)
        
        # Обновляем профиль студента
        student = form.instance.student
        profile, created = StudentProfile.objects.get_or_create(student=student)
        profile.calculate_average_score()
        profile.calculate_nb_count()
        
        messages.success(self.request, 'Оценка успешно выставлена!')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем права доступа
        if request.user.role not in ['teacher', 'decanat']:
            messages.error(request, 'У вас нет прав для выставления оценок')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class JournalView(LoginRequiredMixin, TemplateView):
    """Журнал в формате таблицы с возможностью выставления оценок"""
    template_name = 'journal/journal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        group = self.request.GET.get('group')
        subject = self.request.GET.get('subject')
        
        # Используем правильный подсчёт недель
        week = self.request.GET.get('week')
        if not week:
            week = get_academic_week_number()
        else:
            week = int(week)
        
        year = self.request.GET.get('year', datetime.now().year)
        
        context['groups'] = Student.objects.values_list('group', flat=True).distinct().order_by('group')
        context['subjects'] = Grade.objects.values_list('subject', flat=True).distinct()
        context['current_group'] = group
        context['current_subject'] = subject
        context['current_week'] = week
        context['current_year'] = int(year)
        context['academic_year'] = get_current_academic_year()
        
        if group:
            students = Student.objects.filter(group=group).select_related('user')
            context['students'] = students
            
            if subject and week and year:
                # Получаем оценки за неделю
                grades = Grade.objects.filter(
                    student__group=group,
                    subject=subject,
                    week_number=week,
                    date__year=year
                ).select_related('student__user')
                
                # Группируем по студентам
                journal_data = {}
                for student in students:
                    student_grades = grades.filter(student=student).order_by('date')
                    
                    # Получаем или создаём профиль
                    profile, created = StudentProfile.objects.get_or_create(student=student)
                    if created or profile.average_score == 0:
                        profile.calculate_average_score()
                        profile.calculate_nb_count()
                    
                    journal_data[student.id] = {
                        'student': student,
                        'grades': list(student_grades)
                    }
                
                context['journal_data'] = journal_data
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка выставления оценок"""
        if request.user.role not in ['teacher', 'decanat']:
            messages.error(request, 'У вас нет прав для выставления оценок')
            return redirect('journal:journal')
        
        group = request.GET.get('group')
        subject = request.GET.get('subject')
        date = request.POST.get('date')
        
        if not all([group, subject, date]):
            messages.error(request, 'Заполните все обязательные поля')
            return redirect(f"{request.path}?group={group}&subject={subject}")
        
        # Получаем преподавателя
        teacher = None
        if request.user.role == 'teacher':
            from decanat.models import Teacher
            try:
                teacher = Teacher.objects.get(user=request.user)
            except Teacher.DoesNotExist:
                pass
        
        students = Student.objects.filter(group=group)
        grades_created = 0
        
        for student in students:
            score_key = f'score_{student.id}'
            nb_key = f'nb_{student.id}'
            
            score = request.POST.get(score_key)
            is_nb = nb_key in request.POST
            
            # Преобразуем score в int если есть
            if score:
                try:
                    score = int(score)
                    if score < 1 or score > 12:
                        continue
                except ValueError:
                    continue
            
            if score or is_nb:
                Grade.objects.create(
                    student=student,
                    subject=subject,
                    score=score if not is_nb else None,
                    is_nb=is_nb,
                    date=date,
                    teacher=teacher
                )
                grades_created += 1
                
                # Обновляем профиль
                profile, created = StudentProfile.objects.get_or_create(student=student)
                profile.calculate_average_score()
                profile.calculate_nb_count()
        
        if grades_created > 0:
            messages.success(request, f'Успешно выставлено оценок: {grades_created}')
        else:
            messages.warning(request, 'Оценки не были выставлены')
        
        return redirect(f"{request.path}?group={group}&subject={subject}&week={request.GET.get('week', '')}&year={request.GET.get('year', '')}")
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)