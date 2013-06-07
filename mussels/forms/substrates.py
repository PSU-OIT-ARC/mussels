from django import forms
from mussels.models import Substrate, Status, Type, Waterbody, User, Agency, SubstrateType
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Point

class SubstrateForm(forms.ModelForm):
    lat = forms.FloatField()
    lon = forms.FloatField()
    def __init__(self, *args, **kwargs):
        super(SubstrateForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            point = fromstr(self.instance.geom)
            self.fields['lon'].initial = point[0]
            self.fields['lat'].initial = point[1]

    def save(self, commit=False):
        # convert the lat and lon to a point
        point = Point(self.cleaned_data['lon'], self.cleaned_data['lat'])
        self.instance.geom = point

        super(SubstrateForm, self).save(commit=False)
        self.instance.save()

        # update the many to many table for substrate types
        self.instance.types.clear()
        for type in self.cleaned_data['types']:
            st = SubstrateType(type_id=type.type_id, substrate_id=self.instance.pk)
            st.save()

    class Meta:
        model = Substrate
        fields = (
            'waterbody',
            'status',
            'date_checked',
            'physical_description',
            'agency',
            'clr_substrate_id',
            'types',
        )

class SubstrateRelatedForm(forms.ModelForm):
    delete = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(SubstrateRelatedForm, self).__init__(*args, **kwargs)
        self.related_substrates = []

        if self.instance.pk is None:
            self.fields.pop('delete')
        else:
            # get all the substrates related to this instance. fancy reflection
            # stuff going down here
            model_name = self.instance._meta.object_name.lower()
            filter = {model_name + "_id": self.instance.pk}
            self.related_substrates = Substrate.objects.filter(**filter).select_related(
                'agency',
                'status',
                'types',
                'waterbody',
                'user',
            )

    def save(self, *args, **kwargs):
        if self.cleaned_data.get("delete", False):
            self.instance.delete()
        else:
            super(SubstrateRelatedForm, self).save(*args, **kwargs)


class WaterbodyForm(SubstrateRelatedForm):
    class Meta:
        model = Waterbody
        fields = ('name',)


class TypeForm(SubstrateRelatedForm):
    class Meta:
        model = Type
        fields = ('name',)


class AgencyForm(SubstrateRelatedForm):
    class Meta:
        model = Agency
        fields = ('name',)
