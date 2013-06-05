from django.db import models

class Status(models.Model):
    status_id = models.AutoField(primary_key=True, db_column="status_id")
    text = models.CharField(db_column="status_text", max_length=255)

    class Meta:
        db_table = 'statuses'


class Type(models.Model):
    type_id = models.AutoField(primary_key=True, db_column="type_id")
    name = models.CharField(db_column="type_name", max_length=255)

    class Meta:
        db_table = 'types'


class Waterbody(models.Model):
    waterbody_id = models.AutoField(primary_key=True, db_column="waterbody_id")
    name = models.CharField(db_column="waterbody_name", max_length=255)

    class Meta:
        db_table = 'waterbodies'


class User(models.Model):
    user_id = models.AutoField(primary_key=True, db_column="uid")
    username = models.CharField(db_column="username", max_length=255)
    first_name = models.CharField(db_column="fname", max_length=255)
    last_name = models.CharField(db_column="fname", max_length=255)
    title = models.CharField(db_column="title", max_length=255)
    address1 = models.CharField(db_column="address1", max_length=255)
    address2 = models.CharField(db_column="address2", max_length=255)
    city = models.CharField(db_column="city", max_length=255)
    state = models.CharField(db_column="state", max_length=255)
    zip = models.CharField(db_column="zip", max_length=255)
    phone1 = models.CharField(db_column="phone1", max_length=255)
    phone2 = models.CharField(db_column="phone2", max_length=255)
    email = models.CharField(db_column="email", max_length=255)
    reminder = models.CharField(db_column="reminder", max_length=255)
    winter_hold_start = models.CharField(db_column="winter_hold_start", max_length=255)
    winter_hold_stop = models.CharField(db_column="winter_hold_stop", max_length=255)
    admin_notes = models.CharField(db_column="admin_notes", max_length=255)
    need_new_mesh = models.BooleanField(db_column="need_new_mesh", default=False)
    is_active = models.BooleanField(db_column="active", default=True)

    class Meta:
        db_table = 'users'


class Agency(models.Model):
    agency_id = models.AutoField(primary_key=True, db_column="agency_id")
    name = models.CharField(db_column="agency_name", max_length=255)

    class Meta:
        db_table = 'reporting_agencies'


class Substrate(models.Model):
    substrate_id = models.AutoField(primary_key=True, db_column="substrate_id")
    waterbody = models.ForeignKey(Waterbody, db_column="waterbody_id")
    status = models.ForeignKey(Status, db_column="status_id")
    date_checked = models.DateField(db_column="date_checked")
    physical_description = models.TextField()
    agency = models.ForeignKey(Agency, db_column="agency_id")
    clr_substrate_id = models.IntegerField(db_column="clr_substrate_id")
    user = models.IntegerField(db_column="user_id")

    class Meta:
        db_table = 'substrates'


class SubstrateType(models.Model):
    substrate_id = models.ForeignKey(Substrate, db_column="substrate_id")
    type_id = models.ForeignKey(Type, db_column="type_id")
    
    class Meta:
        db_table = 'substrate_types'


