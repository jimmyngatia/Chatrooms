from django import forms
from django.forms import ModelForm
from .models import Room, Message

class CreateRoomForm(ModelForm):
    class Meta:
        model = Room
        # It's better to list fields explicitly to control order
        fields = ['topic', 'name', 'description']
        
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter room name...', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'What is this room about?', 'rows': 5}),
        }

class CreateMessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body'] # Only show the body, the view handles user and room
        
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Write your message here...',
                'class': 'chat-input-field'
            }),
        }