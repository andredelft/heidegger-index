from django.http import Http404
from django.shortcuts import render
from django.views.generic.detail import DetailView

from heidegger_index.models import Lemma, Work, PageReference
from heidegger_index.utils import match_lemmata
from django.conf import settings

import yaml


def index_view(request):
    return render(
        request,
        "index.html",
        {
            "lemmas": Lemma.objects.all(),
            "works": Work.objects.all(),
        },
    )


class WorkDetailView(DetailView):
    model = Work
    template_name = "work_detail.html"
    context_object_name = "work"

    def _title(self):
        return self.object.csl_json.get("title-short") or self.object.csl_json.get(
            "title"
        )

    def _get_work_lemma(self, work: Work) -> Lemma:
        return Lemma.objects.get(value=self._title(), type="w")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        work = context["work"]
        try:
            work_lemma = self._get_work_lemma(work)
        except Lemma.DoesNotExist:
            pass
        else:
            context["work_lemma"] = work_lemma
        context["page_refs"] = work.pagereference_set.filter(lemma__type=None)
        context["person_list"] = work.pagereference_set.filter(lemma__type="p")
        context["work_list"] = work.pagereference_set.filter(lemma__type="w")
        context["head_title"] = self._title()
        print(context)
        return context

    def render_to_response(self, context, **kwargs):
        if not context["work"].csl_json:
            raise Http404("Work not found")
        else:
            return super().render_to_response(context, **kwargs)


class LemmaDetailView(DetailView):
    model = Lemma
    template_name = "lemma_detail.html"
    context_object_name = "lemma"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lemma = context["lemma"]
        context["children"] = lemma.children.all()
        context["related"] = lemma.related.all()
        if lemma.type == "p":
            context["works"] = lemma.works.all()
        return context
