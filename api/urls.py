from django.urls import path
from .views import *
urlpatterns = [
    path('users/',UserView.as_view(),),
    path('users/<int:id>',UserView.as_view(),),
    path('users/verify-email/',VerifyEmailView.as_view(),),
    path('users/login/',loginView.as_view(),),
    path('users/passwordChange/',PasswordChange.as_view(),),
    path('users/passwordForgot/',ForgotPassword.as_view(),),
    path('users/resetPassword/<uid>/<token>/',ResetPassword.as_view(),),
    path('users/profileData',MyprofileView.as_view(),), 
       
    # path('users/<int:id>',User.as_view(),),    
     
    path('token/refresh/',refreshToken.as_view()),
    
    path('users/dashboard/',DashboardView.as_view(),),
    
    path('vehicles/',VehicleView.as_view()),
    # path('vehicles/<int:id>',VehicleView.as_view()),
    path('vehicles/<int:id>',SingleVehicleView.as_view()),
    
    
    path('drivers/',DriverView.as_view()),
    path('drivers/<int:id>',SingleDriverView.as_view()),
    
    path('managers/',ManagerView.as_view()),
    path('managers/<int:id>',SingleManagerView.as_view()),
    
]
