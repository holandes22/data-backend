from django.conf.urls import url
from django.contrib import admin

from data_api.config.views import ConfigEntryDetail, ConfigEntryList

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/config-entries/$', ConfigEntryList.as_view()),
    url(r'^api/config-entries/(?P<id>[a-zA-Z0-9=]+)/$', ConfigEntryDetail.as_view()),
]
