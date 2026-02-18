from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import CustomUser
from django.contrib import messages


# Create your views here.

def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        gender = request.POST.get("gender")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'register.html')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return render(request, 'register.html')

        user = CustomUser.objects.create_user(
            username=username, 
            email=email, 
            password=password, 
            gender=gender)

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'register.html')

@login_required
def dashboard(request):
    return HttpResponse("Welcome to your dashboard, {}!".format(request.user.username))


def login_view(request):
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']


        if CustomUser.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
        
        elif CustomUser.objects.filter(email=username).exists():
            user_obj = CustomUser.objects.get(email=username)
            user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('login')   # IMPORTANT

    return render(request, 'login.html')

def logout_view(request):
    return HttpResponse("Logged out")