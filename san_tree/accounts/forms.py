from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django import forms
from .models import CustomUsers, Departments, DESIGNATION_CHOICES
import re
from django.core.exceptions import ValidationError

# Registration Form.
class RegisterForm(UserCreationForm):
    employee_id = forms.CharField(max_length=20, required=True)
    department = forms.ModelChoiceField(queryset=Departments.objects.all(), empty_label='select')
    designation = forms.ChoiceField(choices=[('', 'select')] + DESIGNATION_CHOICES)

    class Meta:
        model = CustomUsers
        fields = ['username', 'department', 'designation', 'password1', 'password2', 'employee_id', 'email']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['password2'].label = 'confirm'

        self.fields['email'].required = False

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if not re.fullmatch(r'^[A-Za-z0-9@&!]+$', password):
            raise ValidationError("Password can contain only letters, numbers, and '@'.")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")

        return password

# Login Form.
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password']:
            self.fields[fieldname].help_text = None
            