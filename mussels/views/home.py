import json
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from mussels.models import Specie, Substrate, Waterbody, Agency, Observation, User
from mussels.forms.home import ObservationForm

def home(request):
    species = Specie.objects.all()
    substrates = Substrate.objects.all()
    waterbodies = Waterbody.objects.all()
    agencies = Agency.objects.all()
    waterbodies_json = json.dumps([w.name for w in waterbodies])
    return render(request, "home/home.html", {
        'species': species,
        'substrates': substrates,
        'waterbodies': waterbodies,
        'agencies': agencies,
        'waterbodies_json': waterbodies_json,
    })

def thanks(request):
    return render(request, "home/thanks.html", {
    })

def add(request):
    if request.POST:
        form = ObservationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('thanks'))
    else:
        form = ObservationForm()

    return render(request, "home/add.html", {
        'form': form,
    })
