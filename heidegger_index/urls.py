from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.conf import settings

from heidegger_index.utils import REF_REGEX
from heidegger_index.views import (
    LemmaDetailView,
    index_view,
    WorkDetailView,
    WorkDetailViewMD,
    LemmaDetailViewMD,
    URNRedirectView,
    GNDRedirectView
)

namespaced_patterns = (
    [
        path("", index_view, name="home"),
        path(
            "work/<slug:slug>.md",
            WorkDetailViewMD.as_view(content_type="text/markdown"),
            name="work-md-export",
        ),
        path(
            "work/<slug:slug>/",
            include(
                [
                    path("", WorkDetailView.as_view(), name="work-detail"),
                    re_path(
                        r"(?P<page_range>" + REF_REGEX.pattern + ")",
                        WorkDetailView.as_view(),
                        name="work-detail-select-pages",
                    ),
                ]
            ),
        ),
        path("lemma/<slug:slug>", LemmaDetailView.as_view(), name="lemma-detail"),
        path(
            "lemma/<slug:slug>.md",
            LemmaDetailViewMD.as_view(content_type="text/markdown"),
            name="lemma-md-export",
        ),
        re_path(
            r"^lemma/(?P<urn>urn:cts:([A-Za-z0-9()+,\-.:=@;$_!*']|%[0-9A-Fa-f]{2})+)$",
            URNRedirectView.as_view(),
            name="urn-redirect",
        ),
        re_path(
            r"^gnd/(?P<gnd>1[012]?\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X])$",
            GNDRedirectView.as_view(),
            name="gnd-redirect"
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
