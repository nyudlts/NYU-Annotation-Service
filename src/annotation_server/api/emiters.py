# These classes are represents emiters for HTML and other no standart formats.
from piston.emitters import Emitter, XMLEmitter, JSONEmitter
from django.template import Context, loader
from piston.utils import HttpStatusCode, Mimer
from django.utils.xmlutils import SimplerXMLGenerator
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


def render_to(template, data):
    t = loader.get_template(template)
    c = Context({
        'data': data
    })
    return t.render(c)

class XMLEmitter(XMLEmitter):
    def render(self, request):
        stream = StringIO.StringIO()

        xml = SimplerXMLGenerator(stream, "utf-8")
        xml.startDocument()
        self._to_xml(xml, self.construct())
        xml.endDocument()
        return stream.getvalue()

class HTMLEmitter(Emitter):
   def render(self, request):
       templ = request.GET.get('template', 'default')
       try:
           return render_to('html_emitter/{0}.html'.format(templ), self.data['response']['annotations'])
       except loader.TemplateDoesNotExist:
           return render_to('html_emitter/default.html',  self.data['response']['annotations'])

Emitter.register('xml', XMLEmitter, 'text/xml; charset=utf-8')
Mimer.register(lambda *a: None, ('text/xml',))
#Mimer.register()
