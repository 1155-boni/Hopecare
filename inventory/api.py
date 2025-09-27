from rest_framework import viewsets, permissions
from .models import Item, Stock
from .serializers import ItemSerializer, StockSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['storekeeper', 'admin']:
            return Item.objects.all()
        return Item.objects.none()

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['storekeeper', 'admin']:
            return Stock.objects.all()
        return Stock.objects.none()
