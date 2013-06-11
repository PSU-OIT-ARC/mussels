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
    url(r'^kml/?$', substrates.to_kml, name='substrates-to-kml'),
    url(r'^json/?$', substrates.to_json, name='substrates-to-json'),

    url(r'^admin/?$', substrates.admin, name='substrates-admin'),

    url(r'^admin/substrates/view/?$', substrates.view, name='substrates-view'),
    url(r'^admin/substrates/edit/(\d+)/?$', substrates.edit, name='substrates-edit'),
    url(r'^admin/substrates/add/?$', substrates.edit, name='substrates-edit'),

    url(r'^admin/related/([a-z]+)/?$', substrates.view_related_tables, name='substrates-view-related'),
    url(r'^admin/related/([a-z]+)/add/?$', substrates.edit_related_tables, name='substrates-edit-related'),
    url(r'^admin/related/([a-z]+)/(\d+)/?$', substrates.edit_related_tables, name='substrates-edit-related'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
