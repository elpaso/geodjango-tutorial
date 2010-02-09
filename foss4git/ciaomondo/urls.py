from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'(?P<nome>\w+)', 'ciaomondo.views.default'),
    url(r'^$', 'ciaomondo.views.default'),
)
