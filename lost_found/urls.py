from django.urls import path

from .views import (
    LostFoundItemListView,
    LostFoundItemDetailView,
    MyLostFoundItemsView,
    ClaimQuestionCreateView,
    ClaimAttemptView,
    ClaimAttemptDetailView,
)

urlpatterns = [
    path('my-posts/', MyLostFoundItemsView.as_view(), name='lostfound-my-posts'),
    path('', LostFoundItemListView.as_view(), name='lostfound-list'),
    path('<int:pk>/', LostFoundItemDetailView.as_view(), name='lostfound-detail'),
    path('<int:pk>/claim-questions/', ClaimQuestionCreateView.as_view(), name='lostfound-claim-questions'),
    path('<int:pk>/claims/', ClaimAttemptView.as_view(), name='lostfound-claims'),
    path('claims/<int:pk>/', ClaimAttemptDetailView.as_view(), name='lostfound-claim-detail'),
]

