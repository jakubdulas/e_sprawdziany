from django.shortcuts import render, redirect
from .models import *
from .forms import CreateTestForm
# Create your views here.

def test(request, id):
    context= {

    }

    return render(request, 'test.html', context=context)

def create_test(request):
    form = CreateTestForm()
    if request.method == "POST":
        form = CreateTestForm(request.POST)
        form.instance.teacher = request.user.teacher
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form': form,
    }
    return render(request, 'create_test.html', context=context)