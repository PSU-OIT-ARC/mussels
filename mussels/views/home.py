from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, "home.html")
