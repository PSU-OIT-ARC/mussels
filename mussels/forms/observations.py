from django import forms
from mussels.models import Observation, Specie, Substrate, Waterbody, User, Agency, ObservationSubstrate
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Point

class ObservationSearchForm(forms.Form):
    date_checked = forms.DateField(required=False)
    waterbody = forms.ModelChoiceField(required=False, queryset=Waterbody.objects.all())
    agency = forms.ModelChoiceField(required=False, queryset=Agency.objects.all())
    specie = forms.ModelChoiceField(required=False, queryset=Specie.objects.all())
    user = forms.ModelChoiceField(required=False, queryset=User.objects.all())
    is_approved = forms.TypedChoiceField(required=False, choices=((None, "Any"), (True, "Yes"), (False, "No")), coerce=lambda x: None if x is None or x == "None" else x == "True", empty_value=None)

class ObservationForm(forms.ModelForm):
    lat = forms.FloatField()
    lon = forms.FloatField()
    delete = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(ObservationForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            point = fromstr(self.instance.geom)
            self.fields['lon'].initial = point[0]
            self.fields['lat'].initial = point[1]
        else:
            self.fields.pop("delete")
            # subclasses might not have this field, hence the check
            if "is_approved" in self.fields:
                self.fields['is_approved'].initial = True

    def save(self, commit=False):
        if self.cleaned_data.get("delete", False):
            self.instance.delete()
        else:
            # convert the lat and lon to a point
            point = Point(self.cleaned_data['lon'], self.cleaned_data['lat'])
            self.instance.geom = point

            super(ObservationForm, self).save(commit=False)
            self.instance.save()

            # update the many to many table for substrate types
            self.instance.substrates.clear()
            for substrate in self.cleaned_data['substrates']:
                st = ObservationSubstrate(substrate_id=substrate.substrate_id, observation_id=self.instance.pk)
                st.save()

    class Meta:
        model = Observation
        fields = (
            'waterbody',
            'specie',
            'date_checked',
            'physical_description',
            'agency',
            'substrates',
            'user',
            'is_approved',
        )

class ObservationRelatedForm(forms.ModelForm):
    delete = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(ObservationRelatedForm, self).__init__(*args, **kwargs)
        self.related_observations = []

        if self.instance.pk is None:
            self.fields.pop('delete')
        else:
            # get all the substrates related to this instance. fancy reflection
            # stuff going down here
            model_name = self.instance._meta.object_name.lower()
            # these is a special case for the substrate model, since it is a
            # many2many column
            if model_name == "substrate":
                filter = {"substrates": self.instance.pk}
            else:
                filter = {model_name + "_id": self.instance.pk}

            self.related_observations = Observation.objects.filter(**filter).select_related(
                'agency',
                'specie',
                'substrates',
                'waterbody',
                'user',
            ).prefetch_related("substrates")

    def clean_delete(self):
        delete = self.cleaned_data['delete']
        if delete:
            if len(self.related_observations) != 0:
                raise forms.ValidationError("You cannot delete this when data is associated with it. You must delete the associated data first")
        return delete

    def save(self, *args, **kwargs):
        if self.cleaned_data.get("delete", False):
            self.instance.delete()
        else:
            super(ObservationRelatedForm, self).save(*args, **kwargs)


class WaterbodyForm(ObservationRelatedForm):
    class Meta:
        model = Waterbody
        fields = ('name', 'nhdid')

class SubstrateForm(ObservationRelatedForm):
    class Meta:
        model = Substrate
        fields = ('name', 'order_id', 'machine_name')

class AgencyForm(ObservationRelatedForm):
    class Meta:
        model = Agency
        fields = ('name',)

class SpecieForm(ObservationRelatedForm):
    class Meta:
        model = Specie
        fields = ('name', 'order_id', 'machine_name')

class UserForm(ObservationRelatedForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'title',
            'address1',
            'address2',
            'city',
            'state',
            'zip',
            'phone1',
            'phone2',
            'email',
            'reminder',
            'winter_hold_start',
            'winter_hold_stop',
            'admin_notes',
            'need_new_mesh',
            'is_active',
        )
