from rest_framework import serializers
from .models import Partner, PartnershipCategory, ActivitiesPartner

class PartnershipCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnershipCategory
        fields = '__all__'

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class ActivitiesPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitiesPartner
        fields = '__all__'
