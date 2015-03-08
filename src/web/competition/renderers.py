from django.utils.encoding import smart_unicode
from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, basestring):
            return data
        return smart_unicode(data)


class XMLRenderer(PlainTextRenderer):
    """
    DRF has a built-in XMLRenderer, but it wants to put everything inside of a <root> tag.
    """
    media_type = 'application/xml'
    format = 'xml'


class JSONRenderer(PlainTextRenderer):
    """
    Need a way to quickly pass JSON strings out without running through deserializer.
    """
    media_type = 'application/json'
    format = 'json'