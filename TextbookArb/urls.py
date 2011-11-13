from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TextbookArb.views.home', name='home'),
    # url(r'^TextbookArb/', include('TextbookArb.foo.urls')),
    url(r'^deals/$', 'TextbookArb.ta.views.getDeals'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^launch/$', 'TextbookArb.ta.views.launch'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'TextbookArb.ta.views.loginThing'),
    url(r'^logout/$', 'TextbookArb.ta.views.logout_user'),
    url(r'^lazy/$', 'TextbookArb.ta.views.lazy'),
    url(r'^cats/$', 'TextbookArb.ta.views.defineCategories'),
    url(r'^historical/$', 'TextbookArb.ta.views.getHistoricalPrices'),
)
