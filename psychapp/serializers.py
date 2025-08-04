from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import CustomUser, Cabin, Room, Appointment, CabinPsychologist
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
User = get_user_model()

class CustomCreateUserSerializer(UserCreateSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'password', 'role',
        )

    def create(self, validated_data):
        # Extract the role
        role = validated_data.pop('role')  # Default role if not provided
        user = super().create(validated_data)
        user.role = role
        user.save()
        return user


class CustomUserSerializer(UserSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, read_only=True)
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'email', 'role', 'is_active'
        )
        read_only_fields = ('role', 'is_active')


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = 'id','name'


class CabinPsychologistSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='psychologist.email', read_only=True)
    psychologist_id = serializers.UUIDField(source='psychologist.id', read_only=True)
    class Meta:
        model = CabinPsychologist
        fields = ['psychologist_id', 'email']

class CabinSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)
    cabin_psychologists = CabinPsychologistSerializer(many=True, read_only=True)
    class Meta:
        model = Cabin
        fields = ['id', 'name', 'location', 'rooms', 'cabin_psychologists']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'psychologist', 'client_name', 'date', 'start_time','status']
        read_only_fields = ['psychologist']