import json
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from mussels.models import Specie, Substrate, Waterbody, Agency, Observation

def home(request):
    species = Specie.objects.all()
    substrates = Substrate.objects.all()
    waterbodies = Waterbody.objects.all()
    agencies = Agency.objects.all()
    waterbodies_json = json.dumps([w.name for w in waterbodies])
    return render(request, "home.html", {
        'species': species,
        'substrates': substrates,
        'waterbodies': waterbodies,
        'agencies': agencies,
        'waterbodies_json': waterbodies_json,
    })
