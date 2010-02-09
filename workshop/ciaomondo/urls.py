from django.conf.urls.defaults import *

from ciaomondo.views  import *

urlpatterns = patterns('',
    (r'(?P<nome>\w+)', default_view_nome),
    (r'^$', default_view),
)

