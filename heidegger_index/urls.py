from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings

from heidegger_index.views import LemmaDetailView, index_view, WorkDetailView

heidegger_index_patterns = [
    path("", index_view, name="home"),
    path("work/<slug>", WorkDetailView.as_view(), name="work-detail"),
    path("lemma/<slug>", LemmaDetailView.as_view(), name="lemma-detail"),
]

urlpatterns = [
    path("", RedirectView.as_view(url=settings.URL_PREFIX)),
    path(settings.URL_PREFIX, include(heidegger_index_patterns)),
]
