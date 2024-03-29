from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.conf import settings

from heidegger_index.models import Lemma, PageReference, Work, get_alphabet


def index_view(request):
    alphabet = get_alphabet()

    start = request.GET.get("start")

    if start:
        try:
            start_index = alphabet.index(start)
        except ValueError:
            start_index = 0
    else:
        start_index = 0

    end_index = start_index + settings.PAGINATION_WINDOW
    return render(
        request,
        "lemma_list.html",
        {
            "lemmas": Lemma.objects.alpha_numeric_ordering(
                first_letter__in=alphabet[start_index:end_index], parent=None
            ),
            "works": Work.objects.all(),
            "alphabet": {
                "pre": alphabet[:start_index],
                "selected": alphabet[start_index:end_index],
                "post": alphabet[end_index:],
            },
        },
    )


class WorkDetailView(DetailView):
    model = Work
    template_name = "work_detail.html"
    context_object_name = "work"

    def _get_work_lemma(self, work: Work) -> Lemma:
        return Lemma.objects.get(value=work.title, type="w")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        work = context["work"]
        try:
            work_lemma = self._get_work_lemma(work)
        except Lemma.DoesNotExist:
            pass
        else:
            context["work_lemma"] = work_lemma

        context["index_status"] = work.csl_json.get("index-status", None)

        try:
            page_refs_with_page = []
            for ref in PageReference.objects.filter(
                work__in=[work, *work.children.all()]
            ):
                if ref.refers_to_page_range(self.kwargs["page_range"]):
                    page_refs_with_page.append(ref.id)

            context["page_filter"] = True
            page_refs = PageReference.objects.filter(id__in=page_refs_with_page)
        except KeyError:
            context["page_filter"] = False
            page_refs = PageReference.objects.filter(
                work__in=[work, *work.children.all()]
            )
        context["term_list"] = page_refs.filter(lemma__type=None)
        context["person_list"] = page_refs.filter(lemma__type="p")
        context["work_list"] = page_refs.filter(lemma__type="w")
        return context

    def render_to_response(self, context, **kwargs):
        if not context["work"].csl_json:
            raise Http404("Work not found")
        else:
            return super().render_to_response(context, **kwargs)


class WorkDetailViewMD(WorkDetailView):
    template_name = "markdown/work_detail.md"


class LemmaDetailView(DetailView):
    model = Lemma
    template_name = "lemma_detail.html"
    context_object_name = "lemma"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.work and self.object.type == "w":
            # Redirect Lemma detail page to corresponding work page
            return redirect("work-detail", slug=self.object.work.slug)
        elif self.object.parent:
            # Redirect Lemma detail page to corresponding parent page
            return redirect("lemma-detail", slug=self.object.parent.slug)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lemma = context["lemma"]
        children = lemma.children.all()
        context["children"] = children
        context["related"] = Lemma.objects.filter(related__in=[lemma, *children])
        if lemma.type == "p":
            context["works"] = lemma.works.all()
            context["author_short"] = lemma.value.split(",")[0]
        return context


class LemmaDetailViewMD(LemmaDetailView):
    template_name = "markdown/lemma_detail.md"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class URNRedirectView(LemmaDetailView):
    def get(self, *args, **kwargs):
        lemma = get_object_or_404(Lemma, urn=kwargs["urn"])
        return redirect("lemma-detail", slug=lemma.slug)


class GNDRedirectView(LemmaDetailView):
    def get(self, *args, **kwargs):
        lemma = get_object_or_404(Lemma, gnd=kwargs["gnd"])
        return redirect("lemma-detail", slug=lemma.slug)
