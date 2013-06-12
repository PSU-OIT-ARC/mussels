import datetime
import json
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import fromstr
from django.template.loader import render_to_string
from mussels.forms.observations import ObservationForm, WaterbodyForm, SubstrateForm, AgencyForm
from mussels.models import Observation, Agency, Waterbody, Specie, Substrate

def admin(request):
    return render(request, "observations/admin.html", {

    })

def view(request):
    observations = Observation.objects.all().select_related("waterbody", "agency", "specie", "user").prefetch_related("observationtosubstrate")[:100]
    rendered = render(request, "observations/view.html", {
        'observations': observations,
    })

    return rendered

def edit(request, observation_id=None):
    """
    View for adding or editing a observation observation
    """
    instance = None
    if observation_id is not None:
        instance = get_object_or_404(Observation, observation_id=observation_id)

    if request.POST:
        form = ObservationForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Observation saved")
            return HttpResponseRedirect(reverse("observations-view"))
    else:
        form = ObservationForm(instance=instance)

    return render(request, 'observations/edit.html', {
        'form': form,
    })

model_to_form_class = {
    'waterbody': WaterbodyForm,
    'substrate': SubstrateForm,
    'agency': AgencyForm,
}

model_to_model_class = {
    'waterbody': Waterbody,
    'substrate': Substrate,
    'agency': Agency,
}

def view_related_tables(request, model):
    model_class = model_to_model_class[model]
    objects = model_class.objects.all()
    return render(request, 'observations/view_related.html', {
        'objects': objects,
        'model': model,
    })

def edit_related_tables(request, model, pk=None):
    form_class = model_to_form_class[model]

    instance = None
    related_observations = []
    if pk is not None:
        instance = get_object_or_404(form_class.Meta.model, pk=pk)

    if request.POST:
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Saved!")
            return HttpResponseRedirect(reverse("observations-view-related", args=(model,)))
    else:
        form = form_class(instance=instance)

    return render(request, 'observations/edit_related.html', {
        'form': form,
        'related_observations': related_observations,
    })

def to_kml(request):
    rows = Observation.objects.search(specie="Dreissena r. bugensis")
    string = render_to_string("observations/_kml.kml", {"rows": rows})
    if request.GET:
        response = HttpResponse(string, content_type="text/xml")
    else:
        response = HttpResponse(string, content_type="application/vnd.google-earth.kml+xml; charset=utf-8")
    return response

def to_json(request):
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    kwargs = {}
    if "species[]" in request.GET:
        species = request.GET.getlist("species[]")
        kwargs["species"] = species
    rows = Observation.objects.search(**kwargs)
    for row in rows:
        del row['the_geom']
        p = GEOSGeometry(row['the_geom_plain'])
        row['the_geom_plain'] = (p[0], p[1])
    return HttpResponse(json.dumps(rows, default=dthandler))
