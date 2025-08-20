from rest_framework import serializers
from .models import *
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }
        exclude = ['groups', 'user_permissions']
    
    def create(self, validated_data):
        email = validated_data.get('email')
        role = validated_data.get('role')
        if not email:
            raise serializers.ValidationError({'error': 'Email is required.'})
        if not role:
            raise serializers.ValidationError({'error': 'Role is required.'})

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': 'Email already exists.'})
        
        if role == 'admin':
            user = CustomUser.objects.create_superuser(**validated_data)
        else:
            user = CustomUser.objects.create_user(**validated_data)
            
        return user 

# class loginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ('email','password')
        
class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        
        
class DriverSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    # vehicle_assigned = VehicleSerializer(read_only=True)
    class Meta:
        model = Driver
        fields = '__all__'
        
    def validate(self,validated_data):
        user = validated_data.get('user')
        vehicle = validated_data.get('vehicle_assigned')

        if Driver.objects.filter(user=user).exists():
            raise serializers.ValidationError({'error': 'User already exists.'})
        if self.instance:
            if vehicle == None:
                return validated_data
            
            elif Driver.objects.filter(vehicle_assigned=vehicle).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("This vehicle is already assigned to another driver.")
        else:
            if vehicle != None:    
                if Driver.objects.filter(vehicle_assigned=vehicle).exists():
                    raise serializers.ValidationError({'error': 'Vehicle already assigned.'})
        
        return validated_data
        
        
        
        