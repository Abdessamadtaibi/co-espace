from django.contrib import admin
from .models import Cabin,CabinPsychologist,CustomUser,Appointment

admin.site.register(Cabin)
admin.site.register(CabinPsychologist)
admin.site.register(CustomUser)
admin.site.register(Appointment)