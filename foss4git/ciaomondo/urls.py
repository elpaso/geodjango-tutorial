from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^.*$', 'ciaomondo.views.default'),
    url(r'^$', 'ciaomondo.views.default'),
)
