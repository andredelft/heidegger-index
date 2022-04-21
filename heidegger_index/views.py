from django.shortcuts import render
from django.views.generic.detail import DetailView

from heidegger_index.models import Lemma, Work, PageReference
from django.conf import settings
from fuzzysearch import find_near_matches
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
    def _find_similar_lemmata(self, subject_lemma: Lemma, max_l_dist=2, num_results=3):
        search_term = subject_lemma.value

        with open(settings.BASE_DIR / "index" / "heidegger-index.yml") as f:
            lemmata = yaml.load(f, Loader=yaml.FullLoader).keys()

        # Remove subject lemma from list
        lemmata = [l for l in lemmata if l != search_term]

        matches = [
            (lemma, find_near_matches(search_term, lemma, max_l_dist=max_l_dist))
            for lemma in lemmata
        ]

        # Remove unmatched lemmata from list
        matches = [m for m in matches if m[1]]

        # Sort by levensteihn distance first, then by lemma
        matches.sort(key=lambda match: (min(m.dist for m in match[1]), match[0]))

        similar_lemmata = []
        for match in matches[:num_results]:
            similar_lemmata.append(Lemma.objects.get(value=match[0]))

        # returns list of similar lemma objects
        return similar_lemmata

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["similar_lemmata"] = self._find_similar_lemmata(context["lemma"])
        return context
