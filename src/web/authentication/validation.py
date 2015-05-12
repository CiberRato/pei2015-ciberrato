from validation.models import CaptchaStore
from django.shortcuts import get_object_or_404
from django.http import Http404

def test_captcha(hashkey, response):
    captcha = get_object_or_404(CaptchaStore.objects.all(), hashkey=hashkey)
    if captcha.response != response:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
