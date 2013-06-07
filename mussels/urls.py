from django.conf.urls import patterns, include, url
from views import substrates
from views import home

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mussels.views.home', name='home'),
    # url(r'^mussels/', include('mussels.foo.urls')),
    url(r'^$', home.home, name='home'),
    url(r'^(\d+)/?$', substrates.edit, name='substrates-edit'),
    url(r'^kml/?$', substrates.to_kml, name='substrates-to-kml'),

    url(r'^admin/([a-z]+)?$', substrates.edit_related_tables, name='substrates-edit-related'),
    url(r'^admin/([a-z]+)/(\d+)/?$', substrates.edit_related_tables, name='substrates-edit-related'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
