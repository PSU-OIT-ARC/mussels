from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.db import connection
from django.contrib.auth.models import AbstractBaseUser, UserManager 

class AdminUser(AbstractBaseUser):
    """A custom user model. Not really necessary yet"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, db_index=True)
    email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, blank=True)
    is_superuser = models.BooleanField(default=False, blank=True)
    is_staff = models.BooleanField(default=False, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        db_table = "user"

    #
    # These methods are required to work with Django's admin
    #
    def get_full_name(self): return self.first_name + " " + self.last_name
    def get_short_name(self): return self.first_name + " " + self.last_name

    # we don't need granular permissions; all staff will have access to
    # everything
    def has_perm(self, perm, obj=None): return True
    def has_module_perms(self, app_label): return True


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
    specie_id = models.AutoField(primary_key=True, db_column="specie_id")
    name = models.CharField(db_column="name", max_length=255)
    order_id = models.IntegerField(db_column="order_id", help_text="The order this should appear in on the legend and search form")
    machine_name = models.CharField(db_column="machine_name", max_length=30, help_text="The name used for the map icon")
    is_scientific_name = models.BooleanField(db_column="is_scientific_name", help_text="Determines if italics should be used when displaying on the map", default=False)

    objects = MachineNameManager()

    class Meta:
        db_table = 'specie'
        ordering = ['order_id']

    def __str__(self):
        return self.name


class Substrate(models.Model):
    substrate_id = models.AutoField(primary_key=True, db_column="substrate_id")
    name = models.CharField(db_column="name", max_length=255)
    order_id = models.IntegerField(db_column="order_id", help_text="The order this should appear in on the legend and search form")
    machine_name = models.CharField(db_column="machine_name", max_length=30, help_text="The name used for the map icon")

    objects = MachineNameManager()

    class Meta:
        db_table = 'substrate'
        ordering = ['order_id']

    def __str__(self):
        return self.name


class Waterbody(models.Model):
    waterbody_id = models.AutoField(primary_key=True, db_column="waterbody_id")
    name = models.CharField(db_column="name", max_length=255)
    reachcode = models.CharField(db_column="reachcode", max_length=32, blank=True)

    class Meta:
        db_table = 'waterbody'
        ordering = ['name']

    def __str__(self):
        return self.name


class User(models.Model):
    user_id = models.AutoField(primary_key=True, db_column="user_id")
    username = models.CharField(db_column="username", max_length=255, blank=True)
    first_name = models.CharField(db_column="fname", max_length=255, blank=True)
    last_name = models.CharField(db_column="lname", max_length=255, blank=True)
    title = models.CharField(db_column="title", max_length=255, blank=True)
    address1 = models.CharField(db_column="address1", max_length=255, blank=True)
    address2 = models.CharField(db_column="address2", max_length=255, blank=True)
    city = models.CharField(db_column="city", max_length=255, blank=True)
    state = models.CharField(db_column="state", max_length=255, blank=True)
    zip = models.CharField(db_column="zip", max_length=255, blank=True)
    phone1 = models.CharField(db_column="phone1", max_length=255, blank=True)
    phone2 = models.CharField(db_column="phone2", max_length=255, blank=True)
    email = models.CharField(db_column="email", max_length=255, blank=True)
    reminder = models.CharField(db_column="reminder", max_length=255, blank=True)
    winter_hold_start = models.CharField(db_column="winter_hold_start", max_length=255, blank=True)
    winter_hold_stop = models.CharField(db_column="winter_hold_stop", max_length=255, blank=True)
    admin_notes = models.CharField(db_column="admin_notes", max_length=255, blank=True)
    need_new_mesh = models.BooleanField(db_column="need_new_mesh", default=False)
    is_active = models.BooleanField(db_column="active", default=True)

    class Meta:
        db_table = 'reporter'

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def name(self):
        return str(self)


class Agency(models.Model):
    agency_id = models.AutoField(primary_key=True, db_column="agency_id")
    name = models.CharField(db_column="name", max_length=255)

    class Meta:
        db_table = 'agency'
        ordering = ['name']

    def __str__(self):
        return self.name


class ObservationSubstrate(models.Model):
    substrate_type_id = models.AutoField(db_column="observation_substrate_id", primary_key=True)
    observation = models.ForeignKey('Observation', db_column="observation_id")
    substrate = models.ForeignKey('Substrate', db_column="substrate_id")
    
    class Meta:
        db_table = 'observation_substrate'


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
            observation_id,
            st_AsKML(the_geom, 15) as the_geom,
            st_AsEWKT(the_geom) as the_geom_plain,
            specie.name AS specie,
            string_agg(substrate.name, ', ') AS substrate_type,
            date_checked,
            waterbody.name as waterbody,
            physical_description as description,
            agency.name as agency
            FROM
            observation
            INNER JOIN specie USING(specie_id)
            INNER JOIN waterbody USING(waterbody_id)
            INNER JOIN agency USING(agency_id)
            INNER JOIN observation_substrate USING(observation_id)
            INNER JOIN substrate USING(substrate_id)
            WHERE the_geom IS NOT NULL
            """]
        args = []

        # the caller can pass in kwargs for the search criteria.
        # For each criteria, we add the apprpriate WHERE clause, and append any
        # necessary arguments to the args array
        if "id" in kwargs:
            args.append(kwargs['id'])
            sql.append("AND observation_id = %s")
        if "waterbody" in kwargs:
            args.append(kwargs['waterbody'])
            sql.append("AND waterbody.name = %s")
        if "agency" in kwargs:
            args.append(kwargs['agency'])
            sql.append("AND agency.name = %s")
        if "species" in kwargs:
            # this is the case where the caller wants to return results that
            # have multiple statuses ORd together using a SQL IN()
            # add the IN clause
            sql.append("AND specie.name IN(" + (", ".join(["%s" for _ in kwargs['species']])) + ")")
            # add all the arguments to it
            for specie in kwargs['species']:
                args.append(specie)
        if "substrates" in kwargs:
            # this is the case where the caller wants to return results that
            # have multiple statuses ORd together using a SQL IN()
            # add the IN clause
            sql.append("AND substrate.name IN(" + (", ".join(["%s" for _ in kwargs['substrates']])) + ")")
            # add all the arguments to it
            for specie in kwargs['substrates']:
                args.append(specie)

        has_scientific_name = set([s.machine_name for s in Specie.objects.filter(is_scientific_name=True)])

        sql.append("""
            GROUP BY observation_id,
            ST_AsKML(the_geom, 15),
            st_AsEWKT(the_geom),
            specie.name,
            date_checked,
            waterbody.name,
            physical_description,
            agency.name
        """)

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
            # is scientific name?
            if row['specie_key'] in has_scientific_name:
                row['is_scientific_name'] = True
            rows.append(row)

        return rows


class Observation(models.Model):
    observation_id = models.AutoField(primary_key=True, db_column="observation_id")
    # null=true only because it helps on the PublicObservationForm, when a user
    # enters an "other" waterbody. We don't actually want to store null in this
    # column
    waterbody = models.ForeignKey(Waterbody, db_column="waterbody_id", null=True, blank=True)
    specie = models.ForeignKey(Specie, db_column="specie_id")
    date_checked = models.DateField(db_column="date_checked")
    physical_description = models.TextField()
    # null=true only because it helps on the PublicObservationForm, when a user
    # enters an "other" agency. We don't actually want to store null in this
    # column
    agency = models.ForeignKey(Agency, db_column="agency_id", null=True, blank=True) 
    is_approved = models.BooleanField(db_column="approved", default=False)
    clr_substrate_id = models.IntegerField(db_column="clr_substrate_id", default=0, blank=True)
    user = models.ForeignKey(User, db_column="user_id")
    substrates = models.ManyToManyField(Substrate, through=ObservationSubstrate)

    geom = models.PointField(db_column="the_geom", srid=4326)

    objects = ObservationManager()

    class Meta:
        db_table = 'observation'

    def to_point(self):
        "Convert the geometry of this obversation to a point"
        point = fromstr(self.geom)
        return point

