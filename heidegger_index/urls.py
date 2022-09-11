from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.conf import settings

from heidegger_index.views import LemmaDetailView, index_view, WorkDetailView, WorkDetailViewMD, LemmaDetailViewMD, URNRedirectView

namespaced_patterns = (
    [
        path("", index_view, name="home"),
        path("work/<slug>.md", WorkDetailViewMD.as_view(content_type='text/markdown'), name="work-md-export"),
        path("lemma/<slug>.md", LemmaDetailViewMD.as_view(content_type='text/markdown'), name="lemma-md-export"),
        path("work/<slug>", WorkDetailView.as_view(), name="work-detail"),
        re_path(
            r"^lemma/(?P<urn>urn:cts:([A-Za-z0-9()+,\-.:=@;$_!*']|%[0-9A-Fa-f]{2})+)", 
            URNRedirectView.as_view(),
            name="urn-redirect"
        ),
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
