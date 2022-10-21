from django.urls import path
from . import views

urlpatterns = [
    # USER
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('update-profile', views.updateUser, name="update-user"),


    # DEFAULT
    path('', views.home, name='home'),
    
    # ROOM 
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('room/<str:pk>/', views.room, name='room'),
    
    # MOBILE SITES
    path('topics/', views.topics, name="topics"),
    path('activities/', views.activities, name="activities"),

    # MESSAGE
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message")
]