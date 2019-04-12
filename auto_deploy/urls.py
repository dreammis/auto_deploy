from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.views.generic import TemplateView

from vm.views import handler

urlpatterns = [
    url('^api', csrf_exempt(handler.dispatch)),
    url(r'^vmManager', TemplateView.as_view(template_name="resource/vmManager/index.html", content_type="text/html"))
]
urlpatterns += static('/', document_root='vmManager/dist')
