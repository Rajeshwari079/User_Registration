import random
from django.shortcuts import render, redirect


# Create your views here.

from app.forms import *
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse




def registration(request):
    EUFO=UserForm()
    EPFO=ProfileForm()
    d={'EUFO':EUFO,'EPFO':EPFO}

    if request.method=='POST' and request.FILES:
        NMUFDO=UserForm(request.POST)
        NMPFDO=ProfileForm(request.POST,request.FILES)
        if NMUFDO.is_valid() and NMPFDO.is_valid():
            MFUFDO=NMUFDO.save(commit=False)
            pw=NMUFDO.cleaned_data['password']
            MFUFDO.set_password(pw)
            MFUFDO.save()

            MFPFDO=NMPFDO.save(commit=False)
            MFPFDO.username=MFUFDO
            MFPFDO.save()
            send_mail('registartion',
                      'Thank u for registration',
                      'Kanil40890@gmail.com',
                      [MFUFDO.email],
                      fail_silently=False)

            return HttpResponse('Registartion is Successfull')
        else:
            return HttpResponse('Not valid')


    return render(request,'registration.html',d)


def home(request):
    if request.session.get('username'):
        username=request.session.get('username')
        d={'username':username}
        return render(request,'home.html',d)
    return render(request,'home.html')


def user_login(request):
    if request.method == 'POST':
        username=request.POST['un']
        password=request.POST['pw']

        AUO= authenticate(username=username,password=password)
        if AUO and AUO.is_active:
            login(request,AUO)
            request.session['username']=username
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse('Invalid credentials')
    return render(request,'user_login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def user_profile(request):
    username=request.session['username']
    UO=User.objects.get(username=username)
    PO=Profile.objects.get(username=UO)
    d={'UO':UO, 'PO':PO}
    return render(request,'user_profile.html',d)

@login_required
def change_password(request):
    if request.method == 'POST':
        changePassword=request.POST['cpw']
        username=request.session['username']
        UO=User.objects.get(username=username)
        UO.set_password(changePassword)
        UO.save()
        return HttpResponse('Password is changed')
           
    return render(request,'change_password.html')


def generate_otp():
    return random.randint(1000, 9999)

def otp_generate(request):
    if request.method == 'POST':
        username = request.POST.get('un')
        try:
            user = User.objects.get(username=username)
            genotp = generate_otp()

            # Store OTP and username in session
            request.session['otp'] = str(genotp)
            request.session['username'] = username

            send_mail('Reset Password',
                      f'Your OTP is {genotp}',
                      'rajeshwari.lj2001@gmail.com',
                      [user.email],
                      fail_silently=False)

            return redirect('verify_otp')
        
        except User.DoesNotExist:
            return HttpResponse('User does not exist')

    return render(request, 'otp_generate.html')

def verify_otp(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if input_otp == session_otp:
            return redirect('reset_password')
        else:
            return HttpResponse('Invalid OTP')

    return render(request, 'verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        setpassword = request.POST.get('pw')
        username = request.session.get('username')

        if username:
            user = User.objects.get(username=username)
            user.set_password(setpassword)
            user.save()
            return HttpResponse('Password is set')

    return render(request, 'reset_password.html')
