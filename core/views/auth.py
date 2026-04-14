from django.shortcuts import render, redirect
from django.contrib import messages   # 🔥 ADD THIS
from ..forms import CustomUserCreationForm  

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            messages.success(request, "Account created successfully! Please login.")  # ✅
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")  # ✅

    else:
        form = CustomUserCreationForm()

    return render(request, 'core/signup.html', {'form': form})