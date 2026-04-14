from django.contrib import admin
from .models import *

admin.site.register(Platform)
admin.site.register(Topic)
admin.site.register(Problem)
admin.site.register(UserProblem)