import xlrd
import datetime
from django.db.models import Q
from django.forms import ValidationError
from django.contrib.gis.geos import Point
from .models import Substrate, Waterbody, Specie, User, Agency

def parseObservationsFromFile(path):
    xl = xlrd.open_workbook(path)
    sheet = xl.sheets()[0] 
    columns = [
        'lat',
        'lon',
        'nhdid',
        'waterbody',
        'substrates',
        'specie',
        'date',
        'agency',
        'description',
        'first',
        'last',
        'email',
        'address1',
        'address2',
        'city',
        'state',
        'zip',
        'phone',
    ]

    rows = []
    for row_index in range(1, sheet.nrows):
        rows.append(dict([(k, sheet.cell(row_index, col_index).value) for col_index, k in enumerate(columns)]))

    # try to convert all the rows to appropriate python types, and raise useful
    # errors in necessary
    try:
        for excel_line_number, row in enumerate(rows, 2):
            _to_python(row, datemode=xl.datemode)
    except Substrate.DoesNotExist as e:
        raise ValidationError("The substrate '%s' does not exist in the database. You need to create it, or change your spreadsheet on line %d" % (e.substrate, excel_line_number))
    except Waterbody.DoesNotExist as e:
        raise ValidationError("The waterbody '%s' does not exist in the database. You need to create it, or change your spreadsheet on line %d" % (row['waterbody'] or str(row['nhdid']), excel_line_number))
    except Waterbody.MultipleObjectsReturned as e:
        raise ValidationError("The waterbody '%s' is ambiguous because multiple waterbodies exist in the database with that name. Disambiguate them in the database, or change your spreadsheet on line %d" % (row['waterbody'] or str(row['nhdid']), excel_line_number))
    except Specie.DoesNotExist as e:
        raise ValidationError("The specie '%s' does not exist in the database. You need to create it, or change your spreadsheet on line %d" % (e.specie, excel_line_number))

    return rows

def _to_python(row, datemode):
    """
    Take a list of cells read from an observations spreadsheet, and convert
    them to the correct python type (in place)
    """
    # create a date object from excel's date float
    date_tuple = xlrd.xldate_as_tuple(row['date'], datemode)
    row['date'] = datetime.date(*date_tuple[0:3])

    # convert the substrate string to a list of Substrate objects
    substrates = row['substrates'].strip().split(",")
    values = []
    for substrate in substrates:
        values.append(_to_substrate(substrate))
    row['substrates'] = values

    # convert the waterbody string to a Waterbody object
    row['waterbody'] = _to_waterbody(row['nhdid'], row['waterbody'])

    # convert the specie string to a Specie object
    row['specie'] = _to_specie(row['specie'])

    # agency
    row['agency'] = _to_agency(row['agency'])

    # create a point object out of the lat and lon
    row['point'] = Point(row['lon'], row['lat'])

    # create or find a user object
    row['user'] = _to_user(row['email'], row)

def _to_substrate(substrate):
    """find a Substrate with a name of `substrate`; case insensitive search"""
    substrate = substrate.strip()
    try:
        return Substrate.objects.get(name__iexact=substrate)
    except Substrate.DoesNotExist as e:
        # attach the substrate name to the exception so it can be used in a
        # pretty error message
        e.substrate = substrate
        raise

def _to_waterbody(nhdid, waterbody):
    """
    find a Waterbody with a name of `waterbody` or an nhdid of `nhdid`; case
    insensitive
    """
    waterbody = waterbody.strip()
    nhdid = str(nhdid).strip() 

    if nhdid and waterbody:
        return Waterbody.objects.get(Q(name__iexact=waterbody) | Q(nhdid__iexact=nhdid))
    elif nhdid:
        return Waterbody.objects.get(nhdid__iexact=nhdid)
    elif waterbody:
        return Waterbody.objects.get(name__iexact=waterbody)
    else:
        raise ValueError("nhdid and waterbody can't both be falsey")

def _to_specie(specie):
    """find a Specie with a name of `specie`; case insensitive search"""
    specie = specie.strip()
    try:
        return Specie.objects.get(name__iexact=specie)
    except Specie.DoesNotExist as e:
        # attach the name to the exception so it can be used in a
        # pretty error message
        e.specie = specie
        raise

def _to_agency(agency):
    """find a agency with a name of `agency`; case insensitive search"""
    agency = agency.strip()
    try:
        return Agency.objects.get(name__iexact=agency)
    except Agency.DoesNotExist as e:
        # attach the name to the exception so it can be used in a
        # pretty error message
        e.agency = agency
        raise

def _to_user(email, row):
    """find a user with an email of `email`; case insensitive search"""
    try:
        return User.objects.get(email__iexact=email)
    except User.MultipleObjectsReturned as e:
        return User.objects.filter(email__iexact=email)[0]
    except User.DoesNotExist as e:
        pass

    # create a user since it doesn't exist (but don't save it yet)
    user = User(
        email=email,
        first_name=row['first_name'],
        last_name=row['last_name'],
        address1=row['address1'],
        address2=row['address2'],
        city=row['city'],
        state=row['state'],
        zip=row['zip'],
        phone1=row['phone']
    )
    return user
