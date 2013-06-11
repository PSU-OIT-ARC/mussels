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
from mussels.models import Substrate, Agency, Waterbody, Status, Type

def admin(request):
    return render(request, "substrates/admin.html", {

    })

def view(request):
    substrates = Substrate.objects.all().select_related("waterbody", "agency", "status", "user").prefetch_related("types")[:100]
    rendered = render(request, "substrates/view.html", {
        'substrates': substrates,
    })

    return rendered

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
            return HttpResponseRedirect(reverse("substrates-view"))
    else:
        form = SubstrateForm(instance=instance)

    return render(request, 'substrates/edit.html', {
        'form': form,
    })

model_to_form_class = {
    'waterbody': WaterbodyForm,
    'type': TypeForm,
    'agency': AgencyForm,
}

model_to_model_class = {
    'waterbody': Waterbody,
    'type': Type,
    'agency': Agency,
}

def view_related_tables(request, model):
    model_class = model_to_model_class[model]
    objects = model_class.objects.all()
    return render(request, 'substrates/view_related.html', {
        'objects': objects,
        'model': model,
    })

def edit_related_tables(request, model, pk=None):
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
            return HttpResponseRedirect(reverse("substrates-view-related", args=(model,)))
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
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    kwargs = {}
    if "statuses[]" in request.GET:
        statuses = request.GET.getlist("statuses[]")
        kwargs["statuses"] = statuses
    rows = Substrate.objects.search(**kwargs)
    for row in rows:
        del row['the_geom']
        p = GEOSGeometry(row['the_geom_plain'])
        row['the_geom_plain'] = (p[0], p[1])
    return HttpResponse(json.dumps(rows, default=dthandler))
