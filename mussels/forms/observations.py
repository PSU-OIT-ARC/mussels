from django import forms
from mussels.models import Observation, Specie, Substrate, Waterbody, User, Agency, ObservationSubstrate
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Point

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

class PublicObservationForm(ObservationForm):
    other_waterbody = forms.CharField(max_length=255, required=False)
    other_agency = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(max_length=255, required=False, widget=forms.widgets.TextInput(attrs={"size": 40}))

    #first_name = forms.CharField(max_length=255, required=False)
    #last_name = forms.CharField(max_length=255, required=False)
    #address_1 = forms.CharField(max_length=255, required=False)
    #address_2 = forms.CharField(max_length=255, required=False)
    #city = forms.CharField(max_length=255, required=False)
    #state = forms.CharField(max_length=255, required=False)
    #zip = forms.CharField(max_length=255, required=False)
    #phone = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Observation
        fields = (
            'waterbody',
            'specie',
            'date_checked',
            'physical_description',
            'agency',
            'substrates',
        )
        widgets = {'specie': forms.widgets.RadioSelect}

    def __init__(self, *args, **kwargs):
        super(PublicObservationForm, self).__init__(*args, **kwargs)
        self.fields['waterbody'].choices = list(self.fields['waterbody'].choices)
        self.fields['waterbody'].choices[0] = ("", "Other (specify below)")
        self.fields['waterbody'].widget.attrs.update({"size": 10})
        self.fields['waterbody'].null = True

        self.fields['specie'].choices = list(self.fields['specie'].choices)[1:]

        self.fields['agency'].choices = list(self.fields['agency'].choices)
        self.fields['agency'].choices[0] = ("", "Other (specify below)")
        self.fields['agency'].widget.attrs.update({"size": 10})

        self.fields['physical_description'].widget.attrs.update({"rows": 3})

        self.fields['physical_description'].required = False
        self.fields['date_checked'].required = False

    def clean(self):
        cleaned_data = super(PublicObservationForm, self).clean()
        # if the other waterbody field is filled out, then don't show errors
        # for the waterbody field
        if cleaned_data.get("other_waterbody"):
            self._errors.pop('waterbody', None)
        # same story for agency
        if cleaned_data.get("other_agency"):
            self._errors.pop('agency', None)

        # if the first option of the waterbodies is selected, that means the
        # "other" textbox is required
        if not cleaned_data.get("waterbody") and not cleaned_data.get("other_waterbody"):
            self._errors['waterbody'] = self.error_class(["You must select a waterbody, or specify one in the textbox below"])
        # same for agency
        if not cleaned_data.get("agency") and not cleaned_data.get("other_agency"):
            self._errors['agency'] = self.error_class(["You must select an agency, or specify one in the textbox below"])


        # mutual exclusion for waterbody and other_waterbody fields
        if cleaned_data.get("waterbody") and cleaned_data.get("other_waterbody"):
            self.errors['waterbody'] = self.error_class(["You must either select a waterbody, or specify one in the textbox below. Not both."])
        # same for agency
        if cleaned_data.get("agency") and cleaned_data.get("other_agency"):
            self.errors['agency'] = self.error_class(["You must either select an agency, or specify one in the textbox below. Not both."])

        return cleaned_data

    def save(self, *args, **kwargs):
        # do we need to create the waterbody?
        if not self.cleaned_data.get("waterbody"):
            w = Waterbody(name=self.cleaned_data['other_waterbody'])
            w.save()
            self.instance.waterbody = w
        
        # do we need to create the agency?
        if not self.cleaned_data.get("agency"):
            a = Agency(name=self.cleaned_data['other_agency'])
            a.save()
            self.instance.agency = a

        # find the user, or create it
        email = self.cleaned_data.get("email")
        if email:
            try:
                user = User.objects.filter(email=email)[0]
            except IndexError:
                user = User(email=email)
        else:
            user = User(pk=0)

        self.instance.user = user
        super(PublicObservationForm, self).save(*args, **kwargs)


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
