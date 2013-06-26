from django import forms
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Point
from django.utils.safestring import mark_safe
from mussels.models import Observation, Specie, Substrate, Waterbody, User, Agency, ObservationSubstrate
from mussels.forms import observations

class ObservationForm(observations.ObservationForm):
    other_waterbody = forms.CharField(max_length=255, required=False)
    other_agency = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(max_length=255, required=False, widget=forms.widgets.TextInput(attrs={"size": 40}))

    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    address1 = forms.CharField(max_length=255, required=False)
    address2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=False)
    state = forms.CharField(max_length=255, required=False)
    zip = forms.CharField(max_length=255, required=False)
    phone1 = forms.CharField(max_length=255, required=False)

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
        super(ObservationForm, self).__init__(*args, **kwargs)
        self.fields['waterbody'].choices = list(self.fields['waterbody'].choices)
        self.fields['waterbody'].choices[0] = ("", "Other (specify below)")
        self.fields['waterbody'].widget.attrs.update({"size": 10})
        self.fields['waterbody'].null = True

        # get the specie choices, and make them italic if necessary
        species = Specie.objects.all()
        choices = []
        for specie in species:
            if specie.is_scientific_name:
                choices.append((specie.pk, mark_safe("<em>" + specie.name + "</em>")))
            else:
                choices.append((specie.pk, specie.name))
        self.fields['specie'].choices = choices

        self.fields['agency'].choices = list(self.fields['agency'].choices)
        self.fields['agency'].choices[0] = ("", "Other (specify below)")
        self.fields['agency'].widget.attrs.update({"size": 10})

        self.fields['physical_description'].widget.attrs.update({"rows": 3})

        self.fields['physical_description'].required = False
        self.fields['date_checked'].required = False

    def clean(self):
        cleaned_data = super(ObservationForm, self).clean()
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
            
            # update any user fields that were filled out 
            fields = ('first_name', 'last_name', 'address1', 'address2', 'city', 'state', 'zip', 'phone1')
            for field in fields:
                data = self.cleaned_data.get(field)
                if data is not None:
                    setattr(user, field, data)
                user.save()
        else:
            user = User(pk=0)

        self.instance.user = user
        super(ObservationForm, self).save(*args, **kwargs)

