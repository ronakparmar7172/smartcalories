from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import CustomUser, UserProfile, FoodLog
from django.contrib import messages
from django.utils import timezone

# Create your views here.

        

    
def home(request):
    if not request.user.is_authenticated:
        return render(request, "home.html")
    else:

        profile = request.user.userprofile

        today = timezone.now().date()

        foods = FoodLog.objects.filter(user=request.user, date=today)

        consumed = sum(food.calories for food in foods)
        remaining = profile.calorie_goal - consumed

        percentage = 0
        if profile.calorie_goal > 0:
            percentage = (consumed / profile.calorie_goal) * 100

        context = {
            "profile": profile,
                "foods": foods,
                "consumed": consumed,
                "remaining": remaining,
                "percentage": percentage,
            }

        return render(request, "home.html", context)


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
            return redirect('home')   # IMPORTANT
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('login')   # IMPORTANT

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def profile_view(request):
    return render(request, 'profile_view.html')







@login_required
def edit_profile(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.age = int(request.POST.get("age"))
        profile.height = float(request.POST.get("height"))
        profile.weight = float(request.POST.get("weight"))
        profile.gender = request.POST.get("gender")
        profile.activity_level = request.POST.get("activity_level")

        profile.save()

        return redirect("profile_view")

    return render(request, "edit_profile.html", {"profile": profile})




@login_required
def add_food(request):

    if request.method == "POST":

        food_name = request.POST.get("food_name")
        calories = request.POST.get("calories")
        image = request.FILES.get("image")

        # Case 1: Manual entry
        if food_name and calories:
            FoodLog.objects.create(
                user=request.user,
                food_name=food_name,
                calories=float(calories),
                image=image
            )

        # Case 2: Only image uploaded (AI detection later)
        elif image:
            # Temporary value until AI integration
            predicted_food = "Detected Food"
            predicted_calories = 250  # placeholder

            FoodLog.objects.create(
                user=request.user,
                food_name=predicted_food,
                calories=predicted_calories,
                image=image
            )

        return redirect("home")

    return redirect("home")