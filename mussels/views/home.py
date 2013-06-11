from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from mussels.models import Status, Type

def home(request):
    statuses = Status.objects.all()
    types = Type.objects.all()
    return render(request, "home.html", {
        'statuses': statuses,
        'types': types,
    })
