from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet

router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', ...)

# router.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='review'
# )

# router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comment-list'
# )


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
