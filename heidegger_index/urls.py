from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings

from heidegger_index.views import LemmaDetailView, index_view, WorkDetailView, WorkDetailViewMD

namespaced_patterns = (
    [
        path("", index_view, name="home"),
        path("work/<slug>", WorkDetailView.as_view(), name="work-detail"),
        # TODO: Make sure the plain text does allow unicode characters!
        path("work/<slug>/md", WorkDetailViewMD.as_view(content_type='text/plain'), name="work-md"),
        path("lemma/<slug>", LemmaDetailView.as_view(), name="lemma-detail"),
    ],
    "index",
)

urlpatterns = (
    [
        path("", RedirectView.as_view(url=settings.URL_PREFIX)),
        path(settings.URL_PREFIX, include(namespaced_patterns)),
    ]
    if settings.URL_PREFIX
    else [path("", include(namespaced_patterns))]
)

if settings.DEBUG:
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
