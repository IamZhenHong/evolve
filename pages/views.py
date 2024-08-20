from django.shortcuts import render

# Create your views here.

def home(request):
    # Logic to fetch page content or other data
    return render(request, 'pages/home.html', {'content': 'Welcome to the homepage'})