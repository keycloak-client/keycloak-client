# -*- coding: utf-8 -*-
from django.http import HttpResponse


def home(request):
    user = request.session["user"]
    return HttpResponse(user)


def logout(request):
    return HttpResponse("User logged out successfully")
