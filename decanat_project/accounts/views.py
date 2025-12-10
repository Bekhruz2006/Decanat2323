from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.generic import ListView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, ChangeUsernameForm
from .models import News


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Профиль пользователя"""
    context = {
        'user': request.user
    }
    
    # Добавляем специфичные данные в зависимости от роли
    if request.user.role == 'student':
        try:
            from decanat.models import Student, Curriculum
            from journal.models import StudentProfile
            
            student = Student.objects.get(user=request.user)
            profile, created = StudentProfile.objects.get_or_create(student=student)
            
            if created or profile.average_score == 0:
                profile.calculate_average_score()
                profile.calculate_attendance()
                profile.calculate_nb_count()
            
            context['student'] = student
            context['profile'] = profile
            context['curriculum'] = Curriculum.objects.filter(group=student.group).first()
            context['recent_grades'] = student.grades.all().order_by('-date')[:10]
        except:
            pass
    
    elif request.user.role == 'teacher':
        try:
            from decanat.models import Teacher
            from accounts.models import TeacherGroupAccess
            
            teacher = Teacher.objects.get(user=request.user)
            context['teacher'] = teacher
            context['group_access'] = TeacherGroupAccess.objects.filter(teacher=request.user)
        except:
            pass
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Изменение пароля"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменён!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def change_username_view(request):
    """Изменение логина"""
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if request.user.check_password(password):
                request.user.username = form.cleaned_data['new_username']
                request.user.save()
                messages.success(request, 'Логин успешно изменён!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Неверный пароль!')
    else:
        form = ChangeUsernameForm()
    
    return render(request, 'accounts/change_username.html', {'form': form})


class NewsListView(ListView):
    """Главная страница с новостями"""
    model = News
    template_name = 'accounts/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        return News.objects.all().select_related('author')


def contacts_view(request):
    """Страница контактов"""
    from .models import Contact
    contacts = Contact.objects.filter(is_active=True)
    return render(request, 'accounts/contacts.html', {'contacts': contacts})