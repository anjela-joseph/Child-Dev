from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, ChildProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'phone')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'phone', 'created_at')
        read_only_fields = ('id', 'created_at')


class ChildProfileSerializer(serializers.ModelSerializer):
    age_in_years = serializers.ReadOnlyField()

    class Meta:
        model = ChildProfile
        fields = ('id', 'name', 'date_of_birth', 'gender', 'notes', 'age_in_years', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        validated_data['parent'] = self.context['request'].user
        return super().create(validated_data)
