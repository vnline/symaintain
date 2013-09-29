from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from systack.views import *
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', index,name='index'),
    url(r'^login$',login,name='account_login'),
    url(r'^logout$',logout,name='logout'),
    url(r'^schedule$',schedule,name = 'schedule'),
    url(r'^updatesch/(?P<itemid>[^/]+)/$',updatesch,name= 'updatesch'),
    url(r'^delete/(?P<itemid>[^/]+)/$',delete,name= 'delete'),
    url(r'^finish/(?P<itemid>[^/]+)/$',finish,name= 'finish'),
    url(r'^hotupdate$',hotupdate,name= 'hotupdate$'),
    # url(r'^symaintain/', include('symaintain.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += staticfiles_urlpatterns()