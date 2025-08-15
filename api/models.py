from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
            user.is_active = True
        else:
            user.set_unusable_password()
            user.is_active = False
        user.save()
        
        return user
        
    def create_superuser(self, email, password=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    roles = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('driver', 'Driver'),
    ]
    # id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField( max_length=50)
    last_name = models.CharField( max_length=50)
    role = models.CharField(max_length=10, choices=roles)
    date_of_birth = models.DateField(null=True , blank=True)
    profile_image = models.ImageField(upload_to='profile_image', blank=True, null=True)
    
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("self", on_delete=models.SET_NULL , null=True, blank=True, related_name="created")
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey("self", on_delete=models.SET_NULL , null=True, blank=True, related_name="updated")
    
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    joined_on = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']
    # REQUIRED_FIELDS = ['first_name', 'role']
    
    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.role})'
    
class Vehicle(models.Model):
    types = (
        ("LTV","LTV"),
        ("HTV","HTV"),
    )
    # vehicle_id = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=150)
    vehicle_model = models.CharField(max_length=150)
    vehicle_year = models.IntegerField()
    vehicle_type = models.CharField( max_length= 5,choices= types)
    vehicle_img = models.ImageField( upload_to="vehicle_image", blank=True, null=True)
    chassi_number = models.CharField( max_length=150)
    registration_number = models.CharField(max_length=150)
    vehicle_description = models.TextField( )
    
    status = models.BooleanField(default=False)
    
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,related_name='created_vehicle',blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,null=True,related_name='updated_vehicle',blank=True)

    def __str__(self):
        return self.vehicle_name
    
class Driver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True,related_name="driver_profile")
    driving_license = models.FileField(upload_to="license")
    license_expiry_date = models.DateField()
    vehicle_assigned = models.ForeignKey(Vehicle, null= True , blank=True, on_delete=models.SET_NULL,related_name='vehicle_assigned')
    driver_address = models.TextField()
    driver_experience = models.IntegerField()
    
    
    