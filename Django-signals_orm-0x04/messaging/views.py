from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

@login_required
def delete_user(request):
    user = request.user
    user.delete()
    return redirect('account_deleted')  
