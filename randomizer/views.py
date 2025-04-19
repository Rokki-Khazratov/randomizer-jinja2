from django.shortcuts import render, redirect
import random


def home(request):
    result = request.session.pop('result', None)
    
    if request.method == 'POST':
        try:
            min_num = int(request.POST.get('min_number', 1))
            max_num = int(request.POST.get('max_number', 100))
            if min_num <= max_num:
                result = random.randint(min_num, max_num)
                request.session['result'] = result
                return redirect('randomizer:home')
        except ValueError:
            pass
            
    return render(request, 'home.html', {
        'result': result,
        'min_num': 1,
        'max_num': 100
    })
