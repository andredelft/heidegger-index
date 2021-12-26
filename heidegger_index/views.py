from django.shortcuts import render
from django.views.generic.detail import DetailView

from heidegger_index.models import Lemma, Work


def index_view(request):
    works = Work.objects.all()
    work_ids = set(work.id for work in works if work.reference)
    return render(
        request,
        "index.html",
        {"lemmas": Lemma.objects.all(), "works": works, "work_ids": work_ids},
    )


class WorkDetailView(DetailView):
    model = Work
    template_name = "work_detail.html"
