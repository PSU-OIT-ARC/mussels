# we don't have the django.contrib.auth app installed since we don't want all
# the garbage that comes with it (like groups), but we still want the
# createsuperuser command since it is useful
from django.contrib.auth.management.commands.createsuperuser import Command
