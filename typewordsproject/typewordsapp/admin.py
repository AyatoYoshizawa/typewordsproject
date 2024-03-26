from django.contrib import admin
from .models import Words_Translations, Lesson, List

# Register your models here.
admin.site.register(Words_Translations)
admin.site.register(Lesson)
admin.site.register(List)