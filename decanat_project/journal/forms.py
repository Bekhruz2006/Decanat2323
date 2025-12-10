from django import forms
from .models import Attendance, Grade
from decanat.models import Student


class GradeForm(forms.ModelForm):
    """Форма выставления оценок с балльной системой"""
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'score', 'is_nb', 'date', 'exam_type']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название предмета'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12, 'placeholder': 'Баллы (1-12)'}),
            'is_nb': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exam_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тип контроля'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Если пользователь - преподаватель, ограничиваем выбор студентов
        if user and user.role == 'teacher':
            from accounts.models import TeacherGroupAccess
            teacher_groups = TeacherGroupAccess.objects.filter(
                teacher=user
            ).values_list('group', flat=True)
            
            if teacher_groups:
                self.fields['student'].queryset = Student.objects.filter(
                    group__in=teacher_groups
                )
    
    def clean(self):
        cleaned_data = super().clean()
        score = cleaned_data.get('score')
        is_nb = cleaned_data.get('is_nb')
        
        if is_nb and score:
            raise forms.ValidationError('Нельзя одновременно указать баллы и отметку НБ')
        
        if not is_nb and not score:
            raise forms.ValidationError('Укажите баллы или отметьте НБ')
        
        if score and (score < 1 or score > 12):
            raise forms.ValidationError('Баллы должны быть от 1 до 12')
        
        return cleaned_data


class WeekFilterForm(forms.Form):
    """Форма выбора недели"""
    week = forms.IntegerField(
        label='Номер недели',
        min_value=1,
        max_value=52,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Неделя'})
    )
    year = forms.IntegerField(
        label='Год',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import datetime
        if not self.data:
            self.initial['week'] = datetime.now().isocalendar()[1]
            self.initial['year'] = datetime.now().year


class JournalGradeForm(forms.Form):
    """Форма для массового выставления оценок в журнале"""
    def __init__(self, *args, students=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if students:
            for student in students:
                # Поле для баллов
                self.fields[f'score_{student.id}'] = forms.IntegerField(
                    required=False,
                    min_value=1,
                    max_value=12,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': '1-12'
                    })
                )
                
                # Поле для НБ
                self.fields[f'nb_{student.id}'] = forms.BooleanField(
                    required=False,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )