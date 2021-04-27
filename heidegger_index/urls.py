from django.urls import path

from heidegger_index.views import index_view

urlpatterns = [
    path('', index_view),
]
