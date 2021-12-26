from django.urls import include, path
from django.views.generic import RedirectView

from heidegger_index.views import index_view, WorkDetailView

heidegger_index_patterns = [
    path("", index_view, name="home"),
    path("works/<slug>", WorkDetailView.as_view(), name="work-detail"),
]

urlpatterns = [
    path("", RedirectView.as_view(url="heidegger-index")),
    path("heidegger-index/", include(heidegger_index_patterns)),
]
