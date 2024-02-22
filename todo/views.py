from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import todo_task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

    
def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm})
    else:
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            username = request.POST.get('username')
            try:
                user = User.objects.create_user(username, password=password1)
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'signup.html', {'form': UserCreationForm, 'error': 'Username already exists'})
        else:
            return render(request, 'signup.html', {'form': UserCreationForm, 'error': 'Passwords do not match'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return render(request, 'login.html', {'form': AuthenticationForm, 'error': 'Invalid username or password'})
        else:
            login(request, user)
            return redirect('currenttodos')


@login_required
def logoutuser(request):
    if request.method =='POST':
        logout(request)
        return redirect(home)


@login_required
def createtodo(request):
    if request.method == 'GET': return render(request, 'create.html', {'form': todo_task})
    try:
        form = todo_task(request.POST)
        newtodo = form.save(commit=False)
        newtodo.user = request.user
        newtodo.save()
        return redirect('currenttodos')
    except ValueError: return render(request, 'create.html', {'form': todo_task, 'error': 'value exceed'})


def currenttodos(request):
    a = tasklist.objects.filter(user = request.user,datecompleted__isnull=True)
    return render(request, 'presenttodo.html',{'todos':a})


def completedtodo(request):
    todo = tasklist.objects.filter(user = request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'complete.html',{'todos':todo})

def viewtodo(request, todo_pk):
    todos = get_object_or_404(tasklist, pk=todo_pk, user=request.user)
    todoform = todo_task(instance=todos) if request.method == 'GET' else todo_task(request.POST, instance=todos)
    if request.method == 'POST' and todoform.is_valid():
        todoform.save()
        return redirect('currenttodos')
    return render(request, 'viewtodo.html', {'todo': todos, 'form': todoform, 'error': 'value error' if request.method == 'POST' else None})

def completetodo(request,todo_pk):
    todos = get_object_or_404(tasklist,pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todos.datecompleted = timezone.now()
        todos.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request,todo_pk):
    todos = get_object_or_404(tasklist,pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todos.delete()
        return redirect('currenttodos')