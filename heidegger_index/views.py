from django.http import Http404
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.shortcuts import redirect

from heidegger_index.models import Lemma, Work


def index_view(request):
    lemmas = Lemma.objects.filter(parent=None)
    return render(
        request,
        "index.html",
        {
            "lemmas": lemmas,
            "works": Work.objects.all(),
            "alphabet": sorted(set(lemma.first_letter for lemma in lemmas)),
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.work:
            # Redirect Lemma detail page to corresponding work page
            return redirect("index:work-detail", slug=self.object.work.slug)
        elif self.object.parent:
            return redirect("index:lemma-detail", slug=self.object.parent.slug)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lemma = context["lemma"]
        context["children"] = lemma.children.all()
        context["related"] = lemma.related.all()
        if lemma.type == "p":
            context["works"] = lemma.works.all()
            context["author_short"] = lemma.value.split(",")[0]
        return context
