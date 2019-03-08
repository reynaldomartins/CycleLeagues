from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect, HttpRequest
from django.conf import settings

from django.template import RequestContext
from django.shortcuts import render_to_response

class PermissionErrorMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # print("I got here inside the middleware")
        response = self.get_response(request)
        if isinstance(response, HttpResponseForbidden):
            # print("I got here inside the middleware 2")
            return HttpResponseRedirect("/CLeaguesApp/Error403")
        return response
