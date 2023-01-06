from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.conf import settings

import requests


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
        "index.html",
        {
            "lemmas": Lemma.objects.filter(
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

        page_refs = PageReference.objects.filter(work__in=[work, *work.children.all()])
        context["term_list"] = page_refs.filter(lemma__type=None) | page_refs.filter(lemma__type="g")
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

    def get_object(self, queryset=None):
        """
        CRUDE COPY OF get_object()
        """
        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg)
        gnd = self.kwargs.get('gnd')
        urn = self.kwargs.get('urn')
        if slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})
        if gnd is not None and slug is None:
            queryset = queryset.filter(gnd=gnd)
        if urn is not None and slug is None and gnd is None:
            queryset = queryset.filter(urn=urn)
        # If none of those are defined, it's an error.
        if slug is None and gnd is None and urn is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "slug, urn or gnd in the URLconf." % self.__class__.__name__
            )
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                        {'verbose_name': queryset.model._meta.verbose_name})
        return obj

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
        lemma = context["lemma"]
        return context
