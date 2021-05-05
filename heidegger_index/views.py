from django.shortcuts import render

from heidegger_index.models import Lemma, Work


def index_view(request):
    return render(
        request, 'index.html',
        {
            'lemmas': Lemma.objects.order_by('value'),
            'works': Work.objects.order_by('id')
        }
    )
