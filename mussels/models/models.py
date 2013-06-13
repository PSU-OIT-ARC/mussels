from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.db import connection

# The tables and columns in the database are *very* poorly named, so the
# class name of the models below cannot be used to infer the table name

class MachineNameManager(models.Manager):
    """
    This manager is used on Models that have name and machine_name fields.
    It adds a function to map the name to a machine name
    """
    def to_machine_name(self, name):
        """
        Convert a name to a machine name
        """
        # we cache the mapping to avoid extra db queries
        if (not hasattr(self, "name_to_machine_name")) or (name not in self.name_to_machine_name):
            self.name_to_machine_name = {}
            # fetch the machine names
            rows = self.all()
            for row in rows:
                self.name_to_machine_name[row.name] = row.machine_name
        return self.name_to_machine_name[name]


class Specie(models.Model):
    specie_id = models.AutoField(primary_key=True, db_column="status_id")
    name = models.CharField(db_column="status_text", max_length=255)
    order_id = models.IntegerField(db_column="order_id")
    machine_name = models.CharField(db_column="machine_name", max_length=30)

    objects = MachineNameManager()

    class Meta:
        db_table = 'statuses'
        ordering = ['order_id']

    def __unicode__(self):
        return self.name


class Substrate(models.Model):
    substrate_id = models.AutoField(primary_key=True, db_column="type_id")
    name = models.CharField(db_column="type_name", max_length=255)
    order_id = models.IntegerField(db_column="order_id")
    machine_name = models.CharField(db_column="machine_name", max_length=30)

    objects = MachineNameManager()

    class Meta:
        db_table = 'types'
        ordering = ['order_id']

    def __unicode__(self):
        return self.name


class Waterbody(models.Model):
    waterbody_id = models.AutoField(primary_key=True, db_column="waterbody_id")
    name = models.CharField(db_column="waterbody_name", max_length=255)
    nhdid = models.CharField(db_column="nhdid", max_length=20, verbose_name="NHD ID", blank=True)

    class Meta:
        db_table = 'waterbodies'
        ordering = ['name']

    def __unicode__(self):
        return self.name


class User(models.Model):
    user_id = models.AutoField(primary_key=True, db_column="uid")
    username = models.CharField(db_column="username", max_length=255)
    first_name = models.CharField(db_column="fname", max_length=255)
    last_name = models.CharField(db_column="lname", max_length=255)
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

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def name(self):
        return unicode(self)


class Agency(models.Model):
    agency_id = models.AutoField(primary_key=True, db_column="agency_id")
    name = models.CharField(db_column="agency_name", max_length=255)

    class Meta:
        db_table = 'reporting_agencies'
        ordering = ['name']

    def __unicode__(self):
        return self.name


class ObservationSubstrate(models.Model):
    substrate_type_id = models.AutoField(db_column="substrate_type_id", primary_key=True)
    observation = models.ForeignKey('Observation', db_column="substrate_id")
    substrate = models.ForeignKey('Substrate', db_column="type_id")
    
    class Meta:
        db_table = 'substrate_types'


class ObservationManager(models.GeoManager):
    def search(self, **kwargs):
        """
        Using the display_view view in the database, return all the matching
        data
        """
        # mapping between the columns in the query, and their name
        keys = ["observation_id", "the_geom", "the_geom_plain", "specie", "substrates", "date_checked", "waterbody", "description", "agency"]
        sql = ["""
            SELECT 
                id as observation_id, 
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

        # the caller can pass in kwargs for the search criteria.
        # For each criteria, we add the apprpriate WHERE clause, and append any
        # necessary arguments to the args array
        if "id" in kwargs:
            args.append(kwargs['id'])
            sql.append("AND id = %s")
        if "waterbody" in kwargs:
            args.append(kwargs['waterbody'])
            sql.append("AND waterbody_name = %s")
        if "agency" in kwargs:
            args.append(kwargs['agency'])
            sql.append("AND agency = %s")
        if "species" in kwargs:
            # this is the case where the caller wants to return results that
            # have multiple statuses ORd together using a SQL IN()
            # add the IN clause
            sql.append("AND dv.status IN(" + (", ".join(["%s" for _ in kwargs['species']])) + ")")
            # add all the arguments to it
            for specie in kwargs['species']:
                args.append(specie)
        if "substrates" in kwargs:
            # this is the case where the caller wants to return results that
            # have multiple statuses ORd together using a SQL IN()
            # add the IN clause
            sql.append("AND dv.substrate_type IN(" + (", ".join(["%s" for _ in kwargs['substrates']])) + ")")
            # add all the arguments to it
            for specie in kwargs['substrates']:
                args.append(specie)

        # construct and execute the sql
        sql = " ".join(sql)
        cursor = connection.cursor()
        cursor.execute(sql, args)

        # for each row, build a dict of the row, based on the keys we specified
        # earlier. Then augment it with more information.
        rows = []
        for row in cursor.fetchall():
            row = dict([(k, v) for k, v in zip(keys, row)])
            # add the status machine_name 
            row['specie_key'] = Specie.objects.to_machine_name(row['specie'])
            # add all the machine_names for the types attached to this observation.
            # We want these in sorted order because that is how the icons names
            # are generated
            row['substrate_keys'] = sorted([Substrate.objects.to_machine_name(n) for n in row['substrates'].split(", ")])
            # build up a string that represents the filename of the image for this point
            row['image'] = row['specie_key'] + "_" + "_".join(row['substrate_keys'])
            rows.append(row)

        return rows


class Observation(models.Model):
    observation_id = models.AutoField(primary_key=True, db_column="substrate_id")
    waterbody = models.ForeignKey(Waterbody, db_column="waterbody_id")
    specie = models.ForeignKey(Specie, db_column="status_id")
    date_checked = models.DateField(db_column="date_checked")
    physical_description = models.TextField()
    agency = models.ForeignKey(Agency, db_column="agency_id")
    is_approved = models.BooleanField(db_column="approved", default=False)
    clr_substrate_id = models.IntegerField(db_column="clr_substrate_id", default=0, blank=True)
    user = models.ForeignKey(User, db_column="user_id")
    substrates = models.ManyToManyField(Substrate, through=ObservationSubstrate)

    geom = models.PointField(db_column="the_geom", srid=4326)

    objects = ObservationManager()

    class Meta:
        db_table = 'substrates'

    def to_point(self):
        "Convert the geometry of this obversation to a point"
        point = fromstr(self.geom)
        return point

