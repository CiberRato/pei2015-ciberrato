from captcha.models import CaptchaStore
from django.shortcuts import get_object_or_404
from django.http import Http404


def test_captcha(hashkey, response):
    captcha = get_object_or_404(CaptchaStore.objects.all(), hashkey=hashkey)
    # print captcha.response
    # print response
    if captcha.response != response:
        captcha.delete()
        raise Http404('The captcha response is wrong!')
