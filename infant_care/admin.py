from django.contrib import admin
from .models import FoodIntroduction, AllergySymptomLog, HandoverFolder, MedicationRecord

admin.site.register(FoodIntroduction)
admin.site.register(AllergySymptomLog)
admin.site.register(HandoverFolder)
admin.site.register(MedicationRecord)
