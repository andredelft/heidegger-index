from django.urls import path
from django.views.generic import RedirectView

from heidegger_index.views import index_view

urlpatterns = [
    path("", RedirectView.as_view(url="heidegger-index")),
    path("heidegger-index", index_view),
]
