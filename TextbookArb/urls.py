from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TextbookArb.views.home', name='home'),
    # url(r'^TextbookArb/', include('TextbookArb.foo.urls')),
    url(r'^def/$', 'TextbookArb.ta.views.defineCategories'),
    url(r'^defProxies/$', 'TextbookArb.ta.views.defineProxies'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
