from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login
from .models import Sequence, Number
from .forms import CustomUserCreationForm
import random
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

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
    # Получаем результат из сессии
    result = None
    current_index = request.session.get('current_index', -1)
    error_message = None
    
    print("\n=== Новый запрос ===")
    print(f"Метод: {request.method}")
    print(f"Пользователь: {'Админ' if is_admin(request.user) else 'Обычный'}")
    print(f"Текущий индекс: {current_index}")
    
    # Устанавливаем значения из POST или берем из сессии, или используем дефолтные
    if request.method == 'POST':
        try:
            min_num = int(request.POST.get('min_number', 1))
            max_num = int(request.POST.get('max_number', 100))
            
            print(f"\nПолученные значения:")
            print(f"min_num: {min_num}")
            print(f"max_num: {max_num}")
            
            # Проверка валидности диапазона
            if min_num > max_num:
                error_message = "Минимальное число не может быть больше максимального"
                print(f"\nОшибка валидации: {error_message}")
                min_num = request.session.get('min_number', 1)
                max_num = request.session.get('max_number', 100)
            else:
                request.session['min_number'] = min_num
                request.session['max_number'] = max_num
                print(f"\nЗначения сохранены в сессию: min={min_num}, max={max_num}")
                
                # Проверяем код админа (500)
                if is_admin(request.user) and str(min_num).startswith('500'):
                    print("\nОбнаружен код админа (500)")
                    result = random.randint(min_num, max_num)
                    print(f"Сгенерировано случайное число: {result}")
                
                # Для админа используем последовательность
                elif is_admin(request.user):
                    print("\nПроверка последовательности для админа")
                    active_sequence = Sequence.objects.filter(is_active=True).first()
                    if active_sequence:
                        print(f"Найдена активная последовательность: {active_sequence}")
                        # Получаем все числа последовательности
                        all_numbers = list(active_sequence.numbers.order_by('position').values_list('value', flat=True))
                        print(f"Все числа в последовательности: {all_numbers}")
                        
                        if all_numbers:
                            # Фильтруем числа по максимальному значению
                            valid_numbers = [n for n in all_numbers if n <= max_num]
                            print(f"Отфильтрованные числа (≤{max_num}): {valid_numbers}")
                            
                            if valid_numbers:
                                # Если текущий индекс невалидный, начинаем с начала
                                if current_index < 0 or current_index >= len(valid_numbers):
                                    current_index = -1
                                    print("Сброс индекса на начало")
                                
                                # Получаем следующее число
                                next_index = (current_index + 1) % len(valid_numbers)
                                result = valid_numbers[next_index]
                                
                                # Сохраняем новый индекс
                                request.session['current_index'] = next_index
                                print(f"Результат: индекс {current_index} -> {next_index}, число: {result}")
                            else:
                                print("Нет подходящих чисел после фильтрации")
                        else:
                            print("Последовательность пуста")
                    else:
                        print("Активная последовательность не найдена")
                
                # Для обычных пользователей или если нет активной последовательности
                if result is None:
                    print("\nГенерация случайного числа")
                    result = random.randint(min_num, max_num)
                    print(f"Сгенерировано: {result}")
                
        except ValueError:
            error_message = "Пожалуйста, введите корректные числа"
            print(f"\nОшибка ValueError: {error_message}")
            min_num = request.session.get('min_number', 1)
            max_num = request.session.get('max_number', 100)
    else:
        # Берем значения из сессии или используем дефолтные
        min_num = request.session.get('min_number', 1)
        max_num = request.session.get('max_number', 100)
        print(f"\nЗначения из сессии: min={min_num}, max={max_num}")
    
    # При первом заходе или обновлении страницы сбрасываем индекс последовательности
    if not request.method == 'POST':
        current_index = -1
        request.session['current_index'] = -1
        print("\nСброс индекса последовательности")
            
    print("\n=== Конец запроса ===\n")
    return render(request, 'home.html', {
        'result': result,
        'min_num': min_num,
        'max_num': max_num,
        'error_message': error_message,
        'has_sequence': is_admin(request.user) and Sequence.objects.filter(is_active=True).exists()
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return render(request, 'contact.html')
    
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            request.session['registration_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password1']
            }
            return redirect('randomizer:verify')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def verify(request):
    if request.method == 'POST':
        # In a real application, you would verify the code here
        # For now, we'll just create the user
        registration_data = request.session.get('registration_data')
        if registration_data:
            form = CustomUserCreationForm({
                'username': registration_data['username'],
                'email': registration_data['email'],
                'password1': registration_data['password'],
                'password2': registration_data['password']
            })
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful!')
                del request.session['registration_data']
                return redirect('randomizer:home')
    return render(request, 'verify.html')
