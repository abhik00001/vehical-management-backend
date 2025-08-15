from .serializers import *
from .models import *
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

# def generate_encoded_link(email):
#     uid = urlsafe_base64_encode(force_bytes(email))
#     link = f"http://localhost:5173/verify_email/{uid}"
#     return link

class refreshToken(APIView):
    def post(self,request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access':access_token},status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        name = request.data.get('first_name')
        email = request.data.get('email')
        serializer = UserSerializer(data=request.data)
        uid = urlsafe_base64_encode(force_bytes(email))
        # print(serializer)
        
        if serializer.is_valid():            
            serializer.save(created_by = request.user)
            link = f"http://localhost:5173/verify_email/{uid}"
            send_mail(
                subject= f"Account Creation of {name}",
                message = f"Set Your Password for account creation\n {link}",
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [email],
            )
            return Response({"data":serializer.data,"uid":uid}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    permission_classes = [IsAuthenticated]
    def get(self, request,id):
        user = CustomUser.objects.get(id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self, request,id):
        user = CustomUser.objects.get(id=id)
        serializer = UserSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(updated_by = request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(APIView):
    def post(self, request):
        uid = request.data['email']
        
        email = force_str(urlsafe_base64_decode(uid))
        password = request.data['password']
        
        user = CustomUser.objects.filter(email=email).first()
        driver = Driver.objects.get(user = user.id)
        print(driver)
        serializer = UserSerializer(user)
        if user:
            user.set_password(password)
            # if user.role == 'driver':
            #     if driver.vehicle_assigned != None or driver.vehicle_assigned != '' :
            #         user.is_active = False
            #     else:
            #         user.is_active = True
            # else:
                # user.is_active = True
            user.is_active = True
            user.save()
            return Response({"message": "Email Verified","data":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Email Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
class PasswordChange(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        
        old_password = request.data.get('current')
        password = request.data.get('new')
        confirm_password = request.data.get('confirm')
        if user.check_password(old_password):
            if password == confirm_password:
                user.set_password(password)
                user.save()
                return Response({"message": "Password Changed"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Password and Confirm Password do not match"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Current password do not match"}, status=status.HTTP_404_NOT_FOUND)

class ResetPassword(APIView):
    def post(self, request , uid , token):
        password = request.data['new_password']
        user_id = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(id=user_id)
        if user:
            if not default_token_generator.check_token(user, token):
                return Response({"message": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            return Response({"message": "Password Reset Successfully "}, status=status.HTTP_200_OK)
        return Response({"message": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
class ForgotPassword(APIView):
    def post(self, request):
        email = request.data['email']
        user = CustomUser.objects.get(email=email)
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)
            link = f"http://localhost:5173/reset-password/{uid}/{token}"
            send_mail(
                subject= f"Forgot password of {user.first_name}",
                message = f"Click and Open link for password Reset\n {link}",
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [email],
            )
            return Response({"message": "Email Sent"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
class loginView(APIView): 
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = CustomUser.objects.get(email=email)
        if user:
            serializer = UserSerializer(user)
            if user.is_active == False:
                return Response({"message": "User Not Active"}, status=status.HTTP_401_UNAUTHORIZED)
            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh), 
                    'user': serializer.data,
                    }, status=status.HTTP_200_OK)
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
   
class MyprofileView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        
        #for driver Dashboard
        driver_detail = Driver.objects.filter(user=user).first()
        if driver_detail and driver_detail.vehicle_assigned:
            vehicleDetail = Vehicle.objects.filter(id=driver_detail.vehicle_assigned.id).first()
            vehicleDetail = VehicleSerializer(vehicleDetail)
            
            serializer = UserSerializer(user)
            
            return Response({"message": "Driver Dashboard",'driver_profile': vehicleDetail.data,'user':serializer.data}, status=status.HTTP_200_OK)
            
        #admin     
        total_users = CustomUser.objects.all().count()
        admins = CustomUser.objects.filter(role = 'admin').count()
        
        # managers
        
        managers = CustomUser.objects.filter(role = 'manager').count()
        active_managers = CustomUser.objects.filter(role = 'manager',is_active = True).count()
        unactive_managers = CustomUser.objects.filter(role = 'manager',is_active = False).count()
        userAdded_managers = CustomUser.objects.filter(role='manager',created_by = request.user).count()
        
        # drivers 
        
        drivers = CustomUser.objects.filter(role = 'driver').count()
        assigned_drivers = CustomUser.objects.filter(role = 'driver',is_active = True).count()
        unassigned_drivers = CustomUser.objects.filter(role = 'driver',is_active = False).count()
        userAdded_drivers = CustomUser.objects.filter(role='driver',created_by = request.user).count()
        
        # vehicles
        
        vehicles = Vehicle.objects.all().count()
        userAdded_vehicles = Vehicle.objects.filter(created_by = request.user).count()
        assigned_vehicle = Vehicle.objects.filter(status = True).count()
        unassigned_vehicle = Vehicle.objects.filter(status = False).count()
        
        serializer = UserSerializer(user)
        # print(driver_profile)
        return Response({
            'user': serializer.data,
            'total_users':total_users,
            'total_admins': admins,
            
            'total_vehicles':vehicles,
            'unassigned_vehicle': unassigned_vehicle,
            'assigned_vehicle': assigned_vehicle,
            'userAdded_vehicles':userAdded_vehicles,
            
            'total_drivers': drivers,
            'assigned_drivers':assigned_drivers,
            'unassigned_drivers':unassigned_drivers,
            'userAdded_drivers':userAdded_drivers,
            
            'total_managers': managers,
            'active_managers':active_managers,
            'unactive_managers':unactive_managers,
            'userAdded_managers':userAdded_managers,
        },status=status.HTTP_200_OK)
            
            
# VehicleView
            
class VehicleView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        chassi = request.data.get('chassi_number')
        registration = request.data.get('registration_number')
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            if Vehicle.objects.filter(chassi_number = chassi).exists():
                raise serializers.ValidationError({'error': 'Chassi number already exists.'})
            if Vehicle.objects.filter(registration_number = registration).exists():
                raise serializers.ValidationError({'error': 'Registration number already exists.'})
            serializer.save(created_by = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = CustomUser.objects.all()
        userSerializer = UserSerializer(users, many=True)
        vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return Response({"data":serializer.data,"users":userSerializer.data},status=status.HTTP_200_OK)
    
    
class SingleVehicleView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        try:
            vehicle = Vehicle.objects.get(id=id)
            if vehicle:
                serializer = VehicleSerializer(vehicle)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"error":"Vehicle not found"},status=status.HTTP_404_NOT_FOUND)
            
        except Vehicle.DoesNotExist:
            return Response({"error":"Vehicle not found"},status=status.HTTP_404_NOT_FOUND)
        
    def put(self,request,id):
        data = request.data
        vehicle = Vehicle.objects.get(id=id)
        serializer = VehicleSerializer(vehicle,data = data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by = request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,id):
        vehicle = Vehicle.objects.filter(id=id)
        try:
            vehicle.delete()
            return Response({'message':'vehicle deleted'},status=status.HTTP_200_OK)
        except vehicle.DoesNotExist:
            return Response({'message':'vehicle not found'},status=status.HTTP_404_NOT_FOUND)
        
    def patch(self,request,id):
        vehicle = Vehicle.objects.get(id=id)
        vehicle.status = not vehicle.status
        vehicle.save()
        return Response({'message':'vehicle status updated'},status=status.HTTP_200_OK)
    
    

# DriverView

class DriverView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        all = CustomUser.objects.all()
        allusers = UserSerializer(all,many =True)
        users = CustomUser.objects.filter(role = 'driver')
        userSerializer = UserSerializer(users, many=True)
        drivers = Driver.objects.all()
        driverSerializer = DriverSerializer(drivers,many=True)
        vehicles = Vehicle.objects.all()
        vehicleSerializer = VehicleSerializer(vehicles,many =True)
        return Response({"driverUsers":userSerializer.data,"driverDetail":driverSerializer.data,'vehicles':vehicleSerializer.data,"allusers":allusers.data},status=status.HTTP_200_OK)
    
    def post(self,request):
        uid = request.data.get('user')
        email = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(email = email)
        if Driver.objects.filter(user=user).exists():
            return Response({'message':'driver already exists'},status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        data['user'] = user.id
        if data["vehicle_assigned"] == "":
            data["vehicle_assigned"] = None
            user.is_active = False
            user.save()
        elif data["vehicle_assigned"] != "":
            vehicle = Vehicle.objects.get(id=data["vehicle_assigned"])
            vehicle.status = True
            vehicle.save()
            user.is_active = True
            user.save()
            
        serializer = DriverSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
    
class SingleDriverView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        try:
            driver = Driver.objects.get(id=id)
            serializer = DriverSerializer(driver)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except :
            return Response({'message':'driver not found'},status=status.HTTP_404_NOT_FOUND)
    
    def put(self,request,id):
        try:
            driver = Driver.objects.get(id=id)
            data = request.data
            serializer = DriverSerializer(driver,data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except :
            return Response({'message':'driver not found'},status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        user = CustomUser.objects.filter(id = id)
        user.delete()
        return Response(status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        user = CustomUser.objects.get(id=id)
        try:
            user.is_active = not user.is_active
            user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
# ManagerView
    
class ManagerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = CustomUser.objects.all()
        # managers = CustomUser.objects.filter(role = 'manager')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class SingleManagerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        user = CustomUser.objects.get(id=id)
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'message':'User not found'},status=status.HTTP_404_NOT_FOUND)
        
    def put(self,request,id):
        user = CustomUser.objects.get(id=id)
        data = request.data
        serializer = UserSerializer(user, data=data,partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        user = CustomUser.objects.filter(id = id)
        user.delete()
        return Response(status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
            user.is_active = not user.is_active 
            user.save()
            return Response(status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
