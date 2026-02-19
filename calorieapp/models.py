from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# ----------------------------
# Custom User Model
# ----------------------------
class CustomUser(AbstractUser):

    # Explicit Primary Key (optional, Django already creates this)
    id = models.BigAutoField(primary_key=True)

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username


# ----------------------------
# User Profile (Health Info)
# ----------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    activity_level = models.CharField(max_length=20, null=True, blank=True)

    calorie_goal = models.FloatField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):

        if self.age and self.height and self.weight and self.gender and self.activity_level:

            # BMR formula (Mifflin-St Jeor)
            if self.gender.lower() == "male":
                bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
            else:
                bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161

            multipliers = {
                "low": 1.2,
                "moderate": 1.55,
                "high": 1.9,
            }

            multiplier = multipliers.get(self.activity_level, 1.2)

            self.calorie_goal = round(bmr * multiplier, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Profile"





class FoodLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=200)
    calories = models.FloatField()
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.food_name} - {self.calories} kcal"

