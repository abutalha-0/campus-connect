from django.urls import path

from .views import LostFoundItemListView, LostFoundItemDetailView, MyLostFoundItemsView

urlpatterns = [
    path('my-posts/', MyLostFoundItemsView.as_view(), name='lostfound-my-posts'),
    path('', LostFoundItemListView.as_view(), name='lostfound-list'),
    path('<int:pk>/', LostFoundItemDetailView.as_view(), name='lostfound-detail'),
]
