from django import forms
from .models import ScheduleChange


class ScheduleChangeForm(forms.ModelForm):
    class Meta:
        model = ScheduleChange
        fields = ['original_lesson', 'new_date', 'new_time_slot', 'new_classroom', 'reason', 'is_cancelled']
        widgets = {
            'original_lesson': forms.Select(attrs={'class': 'form-select'}),
            'new_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'new_time_slot': forms.Select(attrs={'class': 'form-select'}),
            'new_classroom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Новая аудитория'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Причина изменения'}),
            'is_cancelled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_date'].required = False
        self.fields['new_time_slot'].required = False
        self.fields['new_classroom'].required = False