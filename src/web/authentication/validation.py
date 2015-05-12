from captcha.models import CaptchaStore
from django.shortcuts import get_object_or_404
from ciberonline.exceptions import BadRequest


def test_captcha(hashkey, response):
    captcha = get_object_or_404(CaptchaStore.objects.all(), hashkey=hashkey)
    if captcha.response != response:
        captcha.delete()
        raise BadRequest('The captcha response is wrong!')