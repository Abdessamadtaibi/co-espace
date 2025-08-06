from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action,APIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.exceptions import PermissionDenied
from .models import Cabin, Room, CustomUser, CabinPsychologist, Appointment
from .serializers import CabinSerializer, RoomSerializer,CabinPsychologistSerializer,AppointmentSerializer
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django.utils.timezone import now
User = get_user_model()

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsPsychologist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'psychologist'


class CabinViewSet(viewsets.ModelViewSet):
    serializer_class = CabinSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Cabin.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        cabin_id = self.kwargs.get('cabin_pk')
        try:
            cabin = Cabin.objects.get(pk=cabin_id)
        except Cabin.DoesNotExist:
            raise NotFound("Cabin not found.")
        return Room.objects.filter(cabin=cabin)

    def perform_create(self, serializer):
        cabin_id = self.kwargs.get('cabin_pk')
        try:
            cabin = Cabin.objects.get(pk=cabin_id)
        except Cabin.DoesNotExist:
            raise NotFound("Cabin not found.")
        serializer.save(cabin=cabin)


class CabinPsychologistViewSet(viewsets.ModelViewSet):
    serializer_class = CabinPsychologistSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        cabin_id = self.kwargs.get('cabin_pk')
        try:
            cabin = Cabin.objects.get(pk=cabin_id)
        except Cabin.DoesNotExist:
            raise NotFound("Cabin not found.")
        return CabinPsychologist.objects.filter(cabin=cabin)

    def perform_create(self, serializer):
        cabin_id = self.kwargs.get('cabin_pk')
        psychologist_id = self.request.data.get('psychologist_id')

        try:
            cabin = Cabin.objects.get(pk=cabin_id)
        except Cabin.DoesNotExist:
            raise NotFound("Cabin not found.")

        try:
            psychologist = User.objects.get(id=psychologist_id, role='psychologist')
        except User.DoesNotExist:
            raise NotFound("Psychologist with this ID not found or not a psychologist.")

        # Prevent duplicates
        if CabinPsychologist.objects.filter(cabin=cabin, psychologist=psychologist).exists():
            raise ValidationError("Psychologist is already assigned to this cabin.")

        serializer.save(cabin=cabin, psychologist=psychologist)




class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPsychologist]

    def get_queryset(self):
        cabin_ids = CabinPsychologist.objects.filter(
            psychologist=self.request.user
        ).values_list('cabin_id', flat=True)
        return Appointment.objects.filter(cabin_id__in=cabin_ids)

    def perform_create(self, serializer):
        user = self.request.user
        try:
            cabin = Cabin.objects.get(cabin_psychologists__psychologist=user)
        except Cabin.DoesNotExist:
            raise NotFound("Cabin not assigned to this psychologist.")
        serializer.save(cabin=cabin,psychologist=user)

    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()
        if appointment.psychologist != request.user:
            raise PermissionDenied("You can only delete your own appointments.")
        return super().destroy(request, *args, **kwargs)

class MyAppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPsychologist]

    def get_queryset(self):
        # Only appointments where the psychologist is the current user
        return Appointment.objects.filter(psychologist=self.request.user)

    def perform_update(self, serializer):
        # Ensure the psychologist cannot change the owner
        serializer.save(psychologist=self.request.user)

    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()
        if appointment.psychologist != request.user:
            raise PermissionDenied("You can only delete your own appointments.")
        return super().destroy(request, *args, **kwargs)