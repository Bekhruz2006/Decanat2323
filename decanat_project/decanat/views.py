from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Student, Curriculum


class StudentListView(ListView):
    model = Student
    template_name = 'decanat/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        search = self.request.GET.get('search', '')
        group = self.request.GET.get('group', '')
        financing = self.request.GET.get('financing', '')
        
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(record_book_number__icontains=search)
            )
        
        if group:
            queryset = queryset.filter(group=group)
        
        if financing:
            queryset = queryset.filter(financing_type=financing)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Student.objects.values_list('group', flat=True).distinct().order_by('group')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_group'] = self.request.GET.get('group', '')
        context['current_financing'] = self.request.GET.get('financing', '')
        return context


class StudentDetailView(DetailView):
    model = Student
    template_name = 'decanat/student_detail.html'
    context_object_name = 'student'
    
    def get_queryset(self):
        return super().get_queryset().select_related('user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Получаем или создаём профиль студента
        from journal.models import StudentProfile
        profile, created = StudentProfile.objects.get_or_create(student=student)
        
        if created or profile.average_score == 0:
            profile.calculate_average_score()
            profile.calculate_attendance()
            profile.calculate_nb_count()
        
        context['profile'] = profile
        context['recent_grades'] = student.grades.all().order_by('-date')[:10]
        context['recent_attendance'] = student.attendances.all().order_by('-date')[:10]
        
        return context


class CurriculumListView(ListView):
    model = Curriculum
    template_name = 'decanat/curriculum_list.html'
    context_object_name = 'curriculums'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        specialty = self.request.GET.get('specialty', '')
        semester = self.request.GET.get('semester', '')
        
        if specialty:
            queryset = queryset.filter(specialty__icontains=specialty)
        
        if semester:
            queryset = queryset.filter(semester=semester)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = Curriculum.objects.values_list('specialty', flat=True).distinct()
        context['semesters'] = range(1, 9)
        context['current_specialty'] = self.request.GET.get('specialty', '')
        context['current_semester'] = self.request.GET.get('semester', '')
        return context