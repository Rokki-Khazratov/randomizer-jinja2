from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Sequence, Number
import random

def is_admin(user):
    return user.is_authenticated and user.is_staff

def get_next_number(numbers, current_index, max_limit=None):
    """
    Получает следующее число из последовательности с учетом максимального лимита
    """
    valid_numbers = numbers if max_limit is None else [n for n in numbers if n <= max_limit]
    
    if not valid_numbers:
        return None, -1
        
    next_index = (current_index + 1) % len(valid_numbers)
    return valid_numbers[next_index], next_index

def home(request):
    result = request.session.pop('result', None)
    current_index = request.session.get('current_index', -1)
    last_max = request.session.get('last_max', None)
    
    # Сбрасываем индекс только при первом заходе или явном обновлении страницы
    if not request.method == 'POST' and not result:
        current_index = -1
        request.session['current_index'] = -1
    
    if request.method == 'POST':
        try:
            min_num = int(request.POST.get('min_number', 1))
            max_num = int(request.POST.get('max_number', 100))
            
            # Сбрасываем индекс если изменился max_num
            if last_max != max_num:
                current_index = -1
                request.session['current_index'] = -1
            
            request.session['last_max'] = max_num
            
            # Проверяем код админа (500)
            if is_admin(request.user) and str(min_num).startswith('500'):
                result = random.randint(min_num, max_num)
                request.session['result'] = result
                return redirect('randomizer:home')
            
            # Для админа используем последовательность
            if is_admin(request.user):
                active_sequence = Sequence.objects.filter(is_active=True).first()
                if active_sequence:
                    # Получаем все числа последовательности
                    all_numbers = list(active_sequence.numbers.order_by('position').values_list('value', flat=True))
                    
                    if all_numbers:
                        # Фильтруем числа по максимальному значению
                        valid_numbers = [n for n in all_numbers if n <= max_num]
                        
                        if valid_numbers:
                            # Если текущий индекс невалидный, начинаем с начала
                            if current_index < 0 or current_index >= len(valid_numbers):
                                current_index = -1
                            
                            # Получаем следующее число
                            next_index = (current_index + 1) % len(valid_numbers)
                            result = valid_numbers[next_index]
                            
                            # Сохраняем новый индекс
                            request.session['current_index'] = next_index
                            request.session['result'] = result
                            
                            print(f"Debug: current_index={current_index}, next_index={next_index}, result={result}, valid_numbers={valid_numbers}, max_num={max_num}")
                            
                            return redirect('randomizer:home')
            
            # Для обычных пользователей или если нет активной последовательности
            if min_num <= max_num:
                result = random.randint(min_num, max_num)
                request.session['result'] = result
                return redirect('randomizer:home')
                
        except ValueError:
            pass
            
    return render(request, 'home.html', {
        'result': result,
        'min_num': 1,
        'max_num': 100,
        'has_sequence': is_admin(request.user) and Sequence.objects.filter(is_active=True).exists()
    })
