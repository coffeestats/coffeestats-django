from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
