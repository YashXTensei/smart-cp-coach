from django.shortcuts import render, redirect
from ..forms import CustomUserCreationForm  

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)   # ✅ custom form
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']   
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'core/signup.html', {'form': form})