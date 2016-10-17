import re
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from .models import User

# Create your views here.
def form_login(request, error_message):
  if request.user.is_authenticated:
    return HttpResponseRedirect(reverse('track:index', args=()))
  return render(request, 'track/auth-login.html', {'next': request.POST.get('next'), 'error_message': error_message})

def auth_login(request):
  username = request.POST.get('username')
  password = request.POST.get('password')
  user = authenticate(username=username, password=password)
  error_message = None
  if user is not None:
    login(request, user)
    return HttpResponseRedirect(request.POST.get('next', '/track'))
  elif password is not None:
    error_message = "Error d'autentificació"
  return form_login(request, error_message)

def auth_logout(request):
  logout(request)
  return HttpResponseRedirect(request.GET.get('next', '/track'))

def auth_register(request):
  error_message = None
  username = request.POST.get('username')
  password =  request.POST.get('password')
  email = request.POST.get('email')
  if username is not None:
    if password == "" or len(password) < 7:
      error_message = 'La contrasenya no és vàlida (mínim 7 caràcters)'
    elif password != request.POST.get('password2'):
      error_message = 'Les contrasenyes no coincideixen'
    elif AuthUser.objects.filter(username=username).count() > 0:
      error_message = 'Ja existeix un usuari amb aquest nom'
    elif re.match(r'[a-z\.\-\_]+@[a-z]+\.[a-z]{2}', email, re.IGNORECASE) is None:
      error_message = 'L\'adreça de correu no és vàlida'
    elif AuthUser.objects.filter(email=email).count() > 0:
      error_message = 'L\'adreça de correu ja està registrada'
    else:
      authuser = AuthUser.objects.create_user(username,
                                              email.lower(),
                                              password)
      authuser.save()

      user = User(avatar_url = '', auth_id = authuser.id)
      user.save()

      return auth_login(request)

  return render(request, 'track/auth-register.html', {'username': username,
                                                      'email': email,
                                                      'error_message': error_message,
                                                      'next': request.POST.get('next')})
