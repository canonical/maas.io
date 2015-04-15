from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import RequestContext, loader, Context


def custom_404(request):
    t = loader.get_template('error/404.html')
    context = RequestContext(request, {'request_path': request.path})
    return HttpResponseNotFound(t.render(context))


def custom_500(request):
    t = loader.get_template('error/500.html')
    return HttpResponseServerError(t.render(Context({})))
