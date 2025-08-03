import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from datetime import datetime, timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username or "", **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, username, **extra_fields)
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('psychologist', 'Psychologist'),
    ]
    username = models.CharField(max_length=50, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def __str__(self):
        return f"{self.email} ({self.role})"

# --------------------------
# Cabin
# --------------------------
class Cabin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cabins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# --------------------------
# CabinPsychologist (Many-to-Many Relationship)
# --------------------------
class CabinPsychologist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cabin = models.ForeignKey(
        Cabin,
        on_delete=models.CASCADE,
        related_name='cabin_psychologists'
    )
    psychologist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_cabin',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'psychologist'}
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['psychologist'], name='unique_psychologist_per_cabin')
        ]

    def __str__(self):
        return f"{self.psychologist.email} in {self.cabin.name}"

class Room(models.Model):
    name = models.CharField(max_length=100)
    cabin = models.ForeignKey(Cabin, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return f"{self.name} (Cabin: {self.cabin.name})"


# --------------------------
# Appointment
# --------------------------
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cabin = models.ForeignKey(Cabin, on_delete=models.CASCADE, related_name='appointments')
    psychologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'psychologist'})
    client_name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_time and not self.end_time:
            dt = datetime.combine(datetime.today(), self.start_time)
            self.end_time = (dt + timedelta(hours=1)).time()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('cabin', 'date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.client_name} - {self.date} ({self.status})"
