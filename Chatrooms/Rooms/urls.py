from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name = "room"),
    path('enroll-room/<str:pk>/', views.enrollRoom, name="enroll-room"),
    path('room/r/createRoom', views.createRoom, name="createRoom"),
    path('room/createMessage/<str:pk>', views.createMessage, name="createMessage"),
    
    path('room/<str:pk>/update', views.updateRoom, name = "updateRoom"),


    path('room/r/<str:pk>/delete', views.deleteRoom, name = "deleteRoom"),
    path('room/m/<str:pk>/delete', views.deleteMessage, name = "deleteMessage"),

    


]