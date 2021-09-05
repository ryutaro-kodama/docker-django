from django.shortcuts import render

# Create your views here.

import datetime

def index(request):
    today = datetime.date.today()
    return render(request, 'sample_app/index.html', {'today': today})