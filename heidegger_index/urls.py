from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.conf import settings

from heidegger_index.views import (
    LemmaDetailView,
    index_view,
    WorkDetailView,
    WorkDetailViewMD,
    LemmaDetailViewMD,
    URNRedirectView,
)

namespaced_patterns = (
    [
        path("", index_view, name="home"),
        path(
            "work/<slug:slug>/",
            include(
                [
                    path("", WorkDetailView.as_view(), name="work-detail"),
                    path(
                        ".md",
                        WorkDetailViewMD.as_view(content_type="text/markdown"),
                        name="work-md-export",
                    ),
                    re_path(
                        r"^(?P<page_range>(?P<page_start>[0-9]{1,4})-?(?P<page_end>[0-9]{0,4})(?P<suffix>[f]{0,2}))$",
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
