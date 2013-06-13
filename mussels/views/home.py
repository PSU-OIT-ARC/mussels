import json
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from mussels.models import Specie, Substrate, Waterbody, Agency, Observation, User
from mussels.forms.observations import PublicObservationForm

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

def thanks(request):
    return HttpResponse("thanks")

def add(request):
    if request.POST:
        form = PublicObservationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('thanks'))
    else:
        form = PublicObservationForm()

    return render(request, "add.html", {
        'form': form,
    })
