import datetime
import json
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import fromstr
from django.template.loader import render_to_string
from mussels.forms.substrates import SubstrateForm, WaterbodyForm, TypeForm, AgencyForm
from mussels.models import Substrate

def edit(request, substrate_id=None):
    """
    View for adding or editing a substrate observation
    """
    instance = None
    if substrate_id is not None:
        instance = get_object_or_404(Substrate, substrate_id=substrate_id)

    if request.POST:
        form = SubstrateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Observation saved")
            return HttpResponseRedirect(reverse("home"))
    else:
        form = SubstrateForm(instance=instance)

    return render(request, 'substrates/edit.html', {
        'form': form,
    })

def edit_related_tables(request, model, pk=None):
    model_to_form_class = {
        'waterbody': WaterbodyForm,
        'type': TypeForm,
        'agency': AgencyForm,
    }
    form_class = model_to_form_class[model]

    instance = None
    related_substrates = []
    if pk is not None:
        instance = get_object_or_404(form_class.Meta.model, pk=pk)

    if request.POST:
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Saved!")
            return HttpResponseRedirect(reverse("home"))
    else:
        form = form_class(instance=instance)

    return render(request, 'substrates/edit_related.html', {
        'form': form,
        'related_substrates': related_substrates,
    })

def to_kml(request):
    rows = Substrate.objects.search(status="Dreissena r. bugensis")
    string = render_to_string("substrates/_kml.kml", {"rows": rows})
    if request.GET:
        response = HttpResponse(string, content_type="text/xml")
    else:
        response = HttpResponse(string, content_type="application/vnd.google-earth.kml+xml; charset=utf-8")
    return response

def to_json(request):
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
    rows = Substrate.objects.search()
    for row in rows:
        del row['the_geom']
        p = GEOSGeometry(row['the_geom_plain'])
        row['the_geom_plain'] = (p[0], p[1])
    return HttpResponse(json.dumps(rows, default=dthandler))
