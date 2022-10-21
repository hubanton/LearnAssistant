from django.shortcuts import render, redirect
from base.models import Room, Topic, Message, User
from django.db.models import Q
from django.http import HttpResponse
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")   

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)   
            return redirect('home') 
        else:
            messages.error(request, "Invalid Password")

    context = {'page' : page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = MyUserCreationForm
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration")


    context = {'page': page, 'form' : form}
    return render(request, 'base/login_register.html', context)



def home(request):

    query = request.GET.get('q') if request.GET.get('q') != None else '' 

    rooms = Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(host__username__icontains=query)
    
    )

    topics = Topic.objects.annotate(num_rooms=Count('room')).order_by('-num_rooms')[0:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))

    context = {"rooms": rooms, "topics": topics, "room_count" : room_count, 'room_messages': room_messages} 
    return render(request, 'base/home.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user, 'rooms' : rooms, 'room_messages': room_messages, 'topics' : topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url="login")
def updateUser(request):
    user = User.objects.get(id=request.user.id)
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
    context = {'form' : form}
    return render(request, 'base/update-user.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            message=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {"room" : room, 'room_messages' : room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)



@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            name=request.POST.get('name'),
            topic=topic,
            description=request.POST.get('description')
        )
        return redirect("home")

    context = {'form' : form, 'topics' : topics}
    return render(request, 'base/room_form.html', context)



@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You do not have access to this room")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST, instance=room)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect("home")

    context = {'form' : form, 'topics' : topics, 'room' : room}
    return render(request, 'base/room_form.html', context)




@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You do not have access to this room")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    context = {'obj' : room}
    return render(request, 'base/delete.html', context)



@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You do not have access to this message")

    if request.method == "POST":
        message.delete()
        return redirect('room', pk=message.room.id)


    context = {'obj' : message}
    return render(request, 'base/delete.html', context)

def topics(request):
    query = request.GET.get('q') if request.GET.get('q') != None else '' 

    topics = Topic.objects.filter(
        Q(name__icontains=query) 
    )
    context = {'topics' : topics}
    return render(request, 'base/topics.html', context)

def activities(request):
    
    activities = Message.objects.all()
    context = {'activities' : activities}
    return render(request, 'base/activities.html', context)