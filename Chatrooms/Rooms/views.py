from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Room, Message, Topic
from .forms import CreateRoomForm, CreateMessageForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'Rooms/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')

    return render(request, 'Rooms/login_register.html', {'page': page})

# --- 1. HOME & SEARCH ---
def home(request):
    
    user = request.user

    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    # Filter rooms by topic name, room name, or description (Case-Insensitive)
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'user': user}
    return render(request, 'Rooms/home.html', context)

# --- 2. ROOM DETAIL & CHAT ---

def room(request, pk):
    room = get_object_or_404(Room, id=pk)
    
    # Check if the user is a participant or the host
    is_participant = room.participants.filter(id=request.user.id).exists()
    
    if not is_participant and request.user != room.host:
        # If not enrolled, show a special 'Access Denied' version of the page
        return render(request, 'Rooms/enroll_notice.html', {'room': room})

    # If they ARE enrolled, show the actual chat
    room_messages = room.messages.all()
    context = {'room': room, 'messages': room_messages}
    return render(request, 'Rooms/room.html', context)

# 2. Add the Enroll view
@login_required(login_url='loginUser')
def enrollRoom(request, pk):
    room = get_object_or_404(Room, id=pk)
    room.participants.add(request.user)
    return redirect('room', pk=room.id)

# @login_required(login_url='loginUser')
def createRoom(request):
    form = CreateRoomForm()
    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user # Automatically set the host to the logged-in user
            room.save()
            return redirect('home')
        
    context = {'form': form}
    return render(request, 'Rooms/create.html', context)

# @login_required(login_url='loginUser')
def updateRoom(request, pk):
    room = get_object_or_404(Room, id=pk)
    
    # Security: Ensure only the host can edit
    if request.user != room.host:
        return HttpResponse('You are not authorized to edit this room.')

    form = CreateRoomForm(instance=room)
    if request.method == 'POST':
        form = CreateRoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
            
    context = {'form': form}
    return render(request, 'Rooms/create.html', context)

# --- 4. MESSAGES ---

from django.http import JsonResponse

@login_required(login_url='loginUser')
def createMessage(request, pk):
    room = get_object_or_404(Room, id=pk)
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body
            )
            room.participants.add(request.user)
            
            # Return JSON data so JS can update the DOM
            return JsonResponse({
                'status': 'success',
                'body': message.body,
                'user': message.user.username,
                'created': "Just now"
            })
            
    return JsonResponse({'status': 'error'}, status=400)# --- 5. DELETION ---
# @login_required(login_url='loginUser')
def deleteRoom(request, pk):
    room = get_object_or_404(Room, id=pk)
    
    if request.user != room.host:
        return HttpResponse('Access Denied')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'Rooms/delete.html', {'object': room})

# @login_required(login_url='loginUser')
def deleteMessage(request, pk):
    message = get_object_or_404(Message, id=pk)

    if request.user != message.user:
        return HttpResponse('Access Denied')

    if request.method == 'POST':
        room_id = message.room.id
        message.delete()
        return redirect('room', pk=room_id)
        
    return render(request, 'Rooms/delete.html', {'object': 'this message'})