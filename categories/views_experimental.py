from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_http_methods

from collections import Counter
import time

from .forms import *
from .models import *
from .monzo_integration import MonzoRequest, NoAccessTokenException
from .views import login_view, process_td_post


class LatestTransactionView(LoginRequiredMixin, generic.TemplateView):
    http_method_names = ['get']
    template_name = 'latest_transaction.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            MonzoRequest()
        except NoAccessTokenException:
            self.request.session['final_redirect'] = reverse(
                'latest_transaction')
            return redirect('login_view')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        t0 = time.time()
        monzo = MonzoRequest()
        latest = monzo.get_latest_transaction()
        req_secs = time.time() - t0

        context['monzo_transaction'] = latest
        context['req_1_secs'] = req_secs
        try:
            context['td'] = Transaction.objects.get(pk=latest['id'])
            context['qs'] = Question.objects.filter(
                category=context['td'].category)
            context['qas'] = QuestionAnswer.objects.filter(td=latest['id'])
        except Transaction.DoesNotExist:
            pass

        return context


class WeekView(LoginRequiredMixin, generic.TemplateView):
    http_method_names = ['get']
    template_name = 'week.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            MonzoRequest()
        except NoAccessTokenException:
            self.request.session['final_redirect'] = reverse('week')
            return redirect('login_view')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        t0 = time.time()
        monzo = MonzoRequest()
        spending = monzo.get_week_of_spends()
        req_1_secs = time.time() - t0

        ids = [t['id'] for t in spending]
        # get any TD objects with a matching ID
        tds = list(Transaction.objects.filter(pk__in=ids))

        # Attach Transaction object to monzo spends if it exists
        for spend in spending:
            spend['td_obj'] = None
            for td in tds:
                if td.id == spend['id']:
                    spend['td_obj'] = td

        # Put the latest transactions at the front of the list
        spending = spending[::-1]

        context['object_list'] = spending
        context['req_1_secs'] = req_1_secs

        return context


class AnalysisView(LoginRequiredMixin, generic.TemplateView):
    http_method_names = ['get']
    template_name = 'analysis.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            MonzoRequest()
        except NoAccessTokenException:
            self.request.session['final_redirect'] = reverse('analysis_view')
            return redirect('login_view')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        monzo = MonzoRequest()
        spending = monzo.get_week_of_spends()

        # sums
        spending_sum_pennies = abs(sum([t['amount'] for t in spending]))

        ingested_spends = monzo.get_week_of_ingested_spends()

        ingested_sum_pennies = abs(sum([t['amount'] for t in ingested_spends]))

        diff = spending_sum_pennies - ingested_sum_pennies

        uningested_transactions = monzo.get_week_of_uningested_spends()
        uningested_sum_pennies = abs(
            sum([t['amount'] for t in uningested_transactions]))

        # some category stuff
        ingested_transactions_monzo = monzo.get_week_of_ingested_spends()
        ingested_transaction_ids = [t['id']
                                    for t in ingested_transactions_monzo]
        ingested_transactions_td = list(
            Transaction.objects.filter(pk__in=ingested_transaction_ids))

        summary = Counter()
        for td in ingested_transactions_td:
            # Get top-level category for each transaction
            category = td.category.parent if td.category.parent else td.category
            monzo_transaction = [
                t for t in ingested_transactions_monzo if t['id'] == td.id][0]
            # spend amounts are always negative
            summary[category.name] -= monzo_transaction['amount']

        context_add = {
            'total_transactions_count': len(spending),
            'spending_sum_pennies': spending_sum_pennies,
            'ingested_sum_pennies': ingested_sum_pennies,
            'count_ingested': len(ingested_spends),
            'diff': diff,
            'uningested_sum_pennies': uningested_sum_pennies,
            'count_uningested': len(uningested_transactions),
            'summary': summary,
        }

        return {**context, **context_add}


@login_required(login_url='/admin/')
@require_http_methods(['GET', 'POST'])
def ingest_view(request):
    if request.method == 'POST':
        return process_td_post(request)

    try:
        monzo = MonzoRequest()
    except NoAccessTokenException:
        request.session['final_redirect'] = reverse('ingest_view')
        return login_view(request)

    transaction = monzo.get_latest_uningested_transaction()
    form_td = TransactionForm(initial={'id': transaction['id']})
    form_qa = QuestionAnswerForm()
    context = {'transaction': transaction,
               'form_td': form_td, 'form_qa': form_qa}
    return render(request, 'ingest.html', context)


@require_http_methods(['GET'])
def category_tree_view(request):
    categories = Category.objects.all()

    top_level_categories = {c: [] for c in categories if not c.parent}
    sub_level_categories = [c for c in categories if c.parent]

    for category in sub_level_categories:
        top_level_categories[category.parent].append(category)

    context = {'object_list': top_level_categories}
    return render(request, 'category_list_tree.html', context)
