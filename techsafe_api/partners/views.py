from rest_framework import viewsets
from .models import Partner, PartnershipCategory, ActivitiesPartner
from .serializers import PartnerSerializer, PartnershipCategorySerializer, ActivitiesPartnerSerializer
from rest_framework.renderers import JSONRenderer

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    renderer_classes = [JSONRenderer]

class PartnershipCategoryViewSet(viewsets.ModelViewSet):
    queryset = PartnershipCategory.objects.all()
    serializer_class = PartnershipCategorySerializer
    renderer_classes = [JSONRenderer]

class ActivitiesPartnerViewSet(viewsets.ModelViewSet):
    queryset = ActivitiesPartner.objects.all()
    serializer_class = ActivitiesPartnerSerializer
    renderer_classes = [JSONRenderer]
