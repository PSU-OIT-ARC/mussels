from django.conf.urls import patterns, include, url
from views import observations
from views import home

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mussels.views.home', name='home'),
    # url(r'^mussels/', include('mussels.foo.urls')),
    url(r'^$', home.home, name='home'),
    url(r'^kml/?$', observations.to_kml, name='observations-to-kml'),
    url(r'^json/?$', observations.to_json, name='observations-to-json'),

    url(r'^admin/?$', observations.admin, name='observations-admin'),

    url(r'^admin/observations/view/?$', observations.view, name='observations-view'),
    url(r'^admin/observations/edit/(\d+)/?$', observations.edit, name='observations-edit'),
    url(r'^admin/observations/add/?$', observations.edit, name='observations-edit'),

    url(r'^admin/related/([a-z]+)/?$', observations.view_related_tables, name='observations-view-related'),
    url(r'^admin/related/([a-z]+)/add/?$', observations.edit_related_tables, name='observations-edit-related'),
    url(r'^admin/related/([a-z]+)/(\d+)/?$', observations.edit_related_tables, name='observations-edit-related'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
