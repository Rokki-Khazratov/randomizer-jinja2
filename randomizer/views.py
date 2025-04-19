from django.shortcuts import render
import random


def home(request):
    result = None
    min_num = None
    max_num = None
    
    if request.method == 'POST':
        try:
            min_num = int(request.POST.get('min_number', 1))
            max_num = int(request.POST.get('max_number', 100))
            if min_num <= max_num:
                result = random.randint(min_num, max_num)
        except ValueError:
            pass
            
    return render(request, 'home.html', {
        'result': result,
        'min_num': min_num,
        'max_num': max_num
    })
