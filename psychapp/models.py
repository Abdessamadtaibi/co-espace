import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# --------------------------
# Custom User Manager
# --------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role="psychologist", **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email, password, role="admin", is_staff=True, is_superuser=True, **extra_fields)

# --------------------------
# User Model
# --------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('psychologist', 'Psychologist'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='psychologist')
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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cabins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# --------------------------
# CabinPsychologist (Many-to-Many Relationship)
# --------------------------
class CabinPsychologist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cabin = models.ForeignKey(Cabin, on_delete=models.CASCADE, related_name='cabin_psychologists')
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'psychologist'})
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cabin', 'psychologist')

    def __str__(self):
        return f"{self.psychologist.email} in {self.cabin.name}"

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
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'psychologist'})
    client_name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('cabin', 'date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.client_name} - {self.date} ({self.status})"
