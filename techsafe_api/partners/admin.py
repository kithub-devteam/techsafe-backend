from django.contrib import admin

from .models import Partner,PartnershipCategory,ActivitiesPartner

admin.site.register(Partner)
admin.site.register(PartnershipCategory)
admin.site.register(ActivitiesPartner)