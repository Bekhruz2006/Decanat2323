from datetime import datetime, date


def get_academic_week_number(target_date=None):
    """
    Получить номер учебной недели от начала учебного года (сентябрь)
    """
    if target_date is None:
        target_date = date.today()
    
    # Определяем начало учебного года
    if target_date.month >= 9:  # С сентября по декабрь
        academic_year_start = date(target_date.year, 9, 1)
    else:  # С января по август
        academic_year_start = date(target_date.year - 1, 9, 1)
    
    # Находим ближайший понедельник от 1 сентября
    days_until_monday = (7 - academic_year_start.weekday()) % 7
    if days_until_monday == 0 and academic_year_start.weekday() != 0:
        days_until_monday = 7
    first_monday = academic_year_start
    if academic_year_start.weekday() != 0:
        from datetime import timedelta
        first_monday = academic_year_start + timedelta(days=days_until_monday)
    
    # Вычисляем номер недели
    if target_date < first_monday:
        return 1
    
    delta = target_date - first_monday
    week_number = (delta.days // 7) + 1
    
    return week_number


def get_current_academic_year():
    """Получить текущий учебный год"""
    today = date.today()
    if today.month >= 9:
        return f"{today.year}/{today.year + 1}"
    else:
        return f"{today.year - 1}/{today.year}"