from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUsers

# Register View.
def RegisterView(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            register_user = form.save(commit=False)

            skip_departments = ['MIS', 'Marketing', 'Operations', 'Engineering & Maintenance', 'Housekeeping', 'Administration', 'Public Relations']
            department_name = register_user.department.name.strip().lower()

            skip_departments_normalized = [d.lower() for d in skip_departments]
            if register_user.designation == 'In Charge':
                if department_name in skip_departments_normalized:
                    register_user.role = 'Admin'
                else:
                    admin_exists = CustomUsers.objects.filter(role = 'Admin', department__name__iexact = register_user.department).exists()
                    if admin_exists:
                        messages.error(request, 'Department has already an admin')
                        return redirect('register')
                    else:
                        register_user.role = 'Admin'
            else:
                register_user.role = 'User'
            register_user.set_password(form.cleaned_data.get('password1'))
            register_user.save()
            
            messages.success(request, 'Registration successful. Please log in.')       
            return redirect('login')
        else:
            messages.error(request, 'please provide valid details.')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {
        'form': form
    })

# Login Form.
def LoginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            login_user = authenticate(request, username=username, password=password)
            if login_user is not None:
                login(request, login_user)
                login_user.refresh_from_db()
                
                if login_user.role == 'Super Admin':
                    return redirect('super_admin')
                else:
                    return redirect('main_dashboard')
            else:
                messages.error(request, 'Invalid Credentials!')
    else:
        form = LoginForm()
    return render(request, 'login.html', {
        'form': form
    })
