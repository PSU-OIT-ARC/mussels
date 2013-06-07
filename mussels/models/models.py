from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.db import connection

class Status(models.Model):
    status_id = models.AutoField(primary_key=True, db_column="status_id")
    name = models.CharField(db_column="status_text", max_length=255)

    class Meta:
        db_table = 'statuses'

    def __unicode__(self):
        return self.name


class Type(models.Model):
    type_id = models.AutoField(primary_key=True, db_column="type_id")
    name = models.CharField(db_column="type_name", max_length=255)

    class Meta:
        db_table = 'types'

    def __unicode__(self):
        return self.name


class Waterbody(models.Model):
    waterbody_id = models.AutoField(primary_key=True, db_column="waterbody_id")
    name = models.CharField(db_column="waterbody_name", max_length=255)

    class Meta:
        db_table = 'waterbodies'

    def __unicode__(self):
        return self.name


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

    def __unicode__(self):
        return self.name


class SubstrateType(models.Model):
    substrate_type_id = models.AutoField(db_column="substrate_type_id", primary_key=True)
    substrate = models.ForeignKey('Substrate', db_column="substrate_id")
    type = models.ForeignKey(Type, db_column="type_id")
    
    class Meta:
        db_table = 'substrate_types'


class SubstrateManager(models.GeoManager):
    STYLE_MAP = {
        'non detect': 'non',
        'results pending': 'pending',
        'Dreissena polymorpha': 'dpoly',
        'Dreissena r. bugensis': 'dbug',
        'D. polymorpha and D. r. bugensis detected': 'both',
        'Unknown': 'unknown',
    }

    def style(self, status, type):
        return SubstrateManager.STYLE_MAP.get(status, "unknown") + "_" + type.lower()
    
    def search(self, **kwargs):
        keys = ["substrate_id", "the_geom", "the_geom_plain", "status", "substrate_type", "date_checked", "waterbody", "description", "agency"]
        sql = ["""
            SELECT 
                id as substrate_id, 
                st_askml(dv.the_geom) as the_geom, 
                st_AsEWKT(dv.the_geom) as the_geom_plain,
                dv.status as status,
                dv.substrate_type as substrate_type, 
                dv.date_checked as date_checked,
                dv.waterbody_name as waterbody, 
                dv.physical_description as description,
                dv.agency as agency 
            FROM 
                public.display_view as dv
            WHERE dv.the_geom IS NOT NULL
        """]
        args = []

        if "type" in kwargs:
            args.append("%" + kwargs['type'] + "%")
            sql.append("AND dv.substrate_type LIKE %s")

        if "status" in kwargs:
            args.append(kwargs['status'])
            sql.append("AND lower(dv.status) = lower(%s)")

        sql = " ".join(sql)
        cursor = connection.cursor()
        cursor.execute(sql, args)

        rows = []
        for row in cursor.fetchall():
            row = dict([(k, v) for k, v in zip(keys, row)])
            types = row['substrate_type'].split(", ")
            for type in types:
                copy = row.copy()
                copy['substrate_type'] = type
                copy['style'] = self.style(copy['status'], copy['substrate_type'])
                rows.append(copy)

        return rows


class Substrate(models.Model):
    substrate_id = models.AutoField(primary_key=True, db_column="substrate_id")
    waterbody = models.ForeignKey(Waterbody, db_column="waterbody_id")
    status = models.ForeignKey(Status, db_column="status_id")
    date_checked = models.DateField(db_column="date_checked")
    physical_description = models.TextField()
    agency = models.ForeignKey(Agency, db_column="agency_id")
    is_approved = models.BooleanField(db_column="approved", default=False)
    clr_substrate_id = models.IntegerField(db_column="clr_substrate_id", default=0, blank=True)
    user = models.IntegerField(db_column="user_id")
    types = models.ManyToManyField(Type, through=SubstrateType)

    geom = models.PointField(db_column="the_geom", srid=4326)

    objects = SubstrateManager()

    class Meta:
        db_table = 'substrates'

    def to_point(self):
        point = fromstr(self.geom)
        return point

