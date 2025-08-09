from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import CustomUser, Cabin, Room, Appointment, CabinPsychologist
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateUserSerializer(UserCreateSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    username = serializers.CharField(required=True)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'password', 're_password', 'role', 'username')

    def validate(self, attrs):
        # Call parent validation first
        attrs = super().validate(attrs)
        
        # Ensure role is present
        if not attrs.get('role'):
            raise serializers.ValidationError({'role': 'This field is required.'})
        
        return attrs

    def create(self, validated_data):
        # Remove re_password from validated_data
        validated_data.pop('re_password', None)
        
        # Create the user
        user = self.Meta.model.objects.create_user(**validated_data)
        return user


class UserSerializer(UserSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'username','email', 'role','is_active',
        )
        read_only_fields = ['role','is_active']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']


class CabinPsychologistSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='psychologist.email', read_only=True)
    psychologist_id = serializers.UUIDField(source='psychologist.id', read_only=True)
    psychologist_username = serializers.UUIDField(source='psychologist.username', read_only=True)

    class Meta:
        model = CabinPsychologist
        fields = ['psychologist_id', 'email', 'psychologist_username']


class CabinSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)
    cabin_psychologists = CabinPsychologistSerializer(many=True, read_only=True)

    class Meta:
        model = Cabin
        fields = ['id', 'name', 'location', 'rooms', 'cabin_psychologists']


class AppointmentSerializer(serializers.ModelSerializer):
    psychologist_username = serializers.UUIDField(source='psychologist.username', read_only=True)
    psychologist_email = serializers.EmailField(source='psychologist.email', read_only=True)
    cabin = serializers.CharField(source='cabin.name', read_only=True)
    class Meta:
        model = Appointment
        fields = ['id', 'psychologist_username','psychologist_email', 'client_name', 'date', 'start_time','status','room','cabin']
        read_only_fields = ['psychologist_username', 'psychologist_email','cabin']