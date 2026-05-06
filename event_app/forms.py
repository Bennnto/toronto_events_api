from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class Registry_Form(UserCreationForm):
    class Meta :
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
        def clean(self):
            cleaned_data = super().clean()
            password1 = cleaned_data.get('password1')
            password2 = cleaned_data.get('password2')
            if password1 and password2 and password1 == password2:
                return password2
            else :
                raise ValueError("Password Not Match")

class Login_Form(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput()) 
    
       