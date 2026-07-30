from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from shared.cloudinary_utils import upload_image
from .models import LostFoundItem
from .serializers import LostFoundItemSerializer


class LostFoundItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        items = LostFoundItem.objects.all()
        item_type = request.query_params.get('item_type')
        status_filter = request.query_params.get('status')
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        date = request.query_params.get('date')
        search = request.query_params.get('search')

        if item_type in ('LOST', 'FOUND'):
            items = items.filter(item_type=item_type)

        if category:
            items = items.filter(category__icontains=category)

        if location:
            items = items.filter(location__icontains=location)

        if date:
            items = items.filter(date_seen=date)

        if status_filter:
            status_value = status_filter.upper()
            if status_value in dict(LostFoundItem.STATUS_CHOICES):
                items = items.filter(status=status_value)
        else:
            items = items.exclude(status='CLOSED')

        if search:
            items = items.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search) |
                Q(category__icontains=search)
            )

        return items

    def get(self, request):
        items = self.get_queryset(request)
        serializer = LostFoundItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        if 'image' in request.FILES:
            data['image_url'] = upload_image(
                request.FILES['image'],
                folder='campus_connect/lost_found'
            )

        serializer = LostFoundItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LostFoundItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)
        serializer = LostFoundItemSerializer(item)
        return Response(serializer.data)

    def patch(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)
        if item.user != request.user and not request.user.is_staff:
            return Response({'detail': 'You can only update your own posts.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        if 'image' in request.FILES:
            data['image_url'] = upload_image(
                request.FILES['image'],
                folder='campus_connect/lost_found'
            )

        serializer = LostFoundItemSerializer(item, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)
        if item.user != request.user and not request.user.is_staff:
            return Response({'detail': 'You can only delete your own posts.'}, status=status.HTTP_403_FORBIDDEN)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyLostFoundItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = LostFoundItem.objects.filter(user=request.user)
        serializer = LostFoundItemSerializer(items, many=True)
        return Response(serializer.data)
