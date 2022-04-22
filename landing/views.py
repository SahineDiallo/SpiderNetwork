from django.shortcuts import render
from django.views import View


class IndexView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'landing/index.html', context)
