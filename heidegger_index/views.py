from django.shortcuts import render
from django.views.generic.detail import DetailView

from heidegger_index.models import Lemma, Work, PageReference
from heidegger_index.utils import match_lemmata
from django.conf import settings


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

    def _get_work_lemma(self, work: Work):
        short_title = work.csl_json.get("title-short")
        if short_title:
            return PageReference.objects.filter(lemma__value=short_title, lemma__type="w")
        else:
            return PageReference.objects.filter(lemma__value=work.csl_json["title"], lemma__type="w")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["work_lemma"] = self._get_work_lemma(context["work"])
        context["page_refs"] = PageReference.objects.filter(work=context["work"])
        context["person_list"] = PageReference.objects.filter(work=context["work"], lemma__type="p")
        context["work_list"] = PageReference.objects.filter(work=context["work"], lemma__type="w")
        return context


class LemmaDetailView(DetailView):
    model = Lemma
    template_name = "lemma_detail.html"
    context_object_name = "lemma"

    # Just a basic copy of index.py find_ref
    def _find_similar_lemmata(self, subject_lemma: Lemma):
        search_term = subject_lemma.value

        matches = match_lemmata(search_term, 2, 3, False)
        similar_lemmata = []
        for match in matches[:3]:
            similar_lemmata.append(Lemma.objects.get(value=match[0]))

        # returns list of similar lemma objects
        return similar_lemmata

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["similar_lemmata"] = self._find_similar_lemmata(context["lemma"])
        return context
