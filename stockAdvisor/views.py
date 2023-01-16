from django.shortcuts import render, redirect
from . import views
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from stockProject import settings
from . import app
from . import models

'''This function returns content that is reusable over
different types of renders of the same page.'''
def page_contents(request):
    favorites = request.user.userwithfavorites.favorites.all()
    return(
        {
            'profile': {'symbols': [{'ticker': x.name, 'plot':app.return_plot(x.name)} for x in favorites]},
            'rebalancer': {'symbols': [x.name for x in favorites]},
        }
    )

# Create your views here.
def home(request):
    try: 
        return render(request, 'stockAdvisor/index.html', {'user': request.user})
    except: 
        return render(request, 'stockAdvisor/index.html')

def rebalancer(request):
    if request.method == 'POST':
        budget = request.POST.get('budget')
        strategy = request.POST.get('strategy')
        data = getattr(app, strategy)(page_contents(request)['rebalancer']['symbols'], float(budget))
        asset_name = data['assets'].keys()
        percentage = [x for x in data['assets'].values()]
        dollar_amount = [x for x in data['assets'].values()]
        for i in range(len(percentage)):
            dollar_amount[i] = dollar_amount[i]['dollar_amount']
            percentage[i] = percentage[i]['percentage_of_portfolio']
        dict = [{'asset': x, 'dollar_amount': y, 'percentage': z} for (x, y, z) in zip(asset_name, dollar_amount, percentage)]
        last = dict.pop(-1)
        return render(request, 'stockAdvisor/rebalancer.html', {
            'data': dict,
            'last': last,
            'pie': app.result_pie(data),
            'strategy': data['strategy'],
            'bar': app.result_bar(data)
        })
    return render(request, 'stockAdvisor/rebalancer.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            return render(request, "stockAdvisor/profile.html", page_contents(request)['profile'])
        else:
            messages.error(request, "Invalid credentials were entered.")
    
    return render(request, 'stockAdvisor/login.html')

def create(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')

        if User.objects.filter(username=username):
            messages.error(request, "The username entered already exists.")
            return redirect('create')
        if User.objects.filter(email=email):
            messages.error(request, "The email entered is already within our sytem.")
            return redirect('create')
        if len(username) > 15 or len(username) < 5:
            messages.error(request, "Usernames must be between 5 and 15 characters long.")
            return redirect('create')
        if not username.isalnum():
            messages.error(request, "Your username must be alphanumeric.")
            return redirect('create')
        if len(pass1) < 8:
            messages.error(request, "Please make a username of at least 8 characters in length.")
            return redirect('create')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.save()
        uwf = models.UserWithFavorites()
        uwf.user = myuser
        uwf.save()

        messages.success(request, "Your Account has been created succesfully!")

        return redirect('login')
    
    return render(request, "stockAdvisor/create.html")

def signout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return render(request, "stockAdvisor/index.html")

def profile(request):
    if request.method == 'POST':
        if request.POST.get('type') == 'add':
            ticker = request.POST.get('symbol_wanted')
            if models.Symbol.objects.filter(name=ticker):
                request.user.userwithfavorites.favorites.add((models.Symbol.objects.get(name=ticker)))
                request.user.userwithfavorites.save()
                messages.success(request, "Successfully Added")
                return redirect('profile')
            else:
                messages.error(request, "Please ensure that you have spelled the ticker's name correctly. We take the ticker of the asset(e.g. AAPL).")
                return redirect('profile')
        elif request.POST.get('type') == 'remove':
            ticker = request.POST.get('symbol_wanted')
            if models.Symbol.objects.filter(name=ticker):
                request.user.userwithfavorites.favorites.remove((models.Symbol.objects.get(name=ticker)))
                request.user.userwithfavorites.save()
                messages.success(request, "Successfully Removed")
                return redirect('profile')
            else:
                messages.error(request, "Please ensure that you have spelled the ticker's name correctly. We take the ticker of the asset(e.g. AAPL).")
                return redirect('profile')
    if request.user.is_authenticated:
        return render(request, "stockAdvisor/profile.html", page_contents(request)['profile'])
    else:
        return render(request, "stockAdvisor/profile.html")