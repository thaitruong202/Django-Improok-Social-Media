from django.urls import path, re_path, include
from rest_framework import routers

from .views import RoleViewSet, UserViewSet, PostViewSet, \
    AccountViewSet, PostImageViewSet, CommentViewSet, ConfirmStatusViewSet, AlumniAccountViewSet, ReactionViewSet, \
    PostReactionViewSet, InvitationGroupViewSet, PostInvitationViewSet, SendEmailView


router = routers.DefaultRouter()
router.register('roles', RoleViewSet, basename='roles')

router.register('confirm_status', ConfirmStatusViewSet, basename='confirm_status')

router.register('users', UserViewSet, basename='users')

# post/{post_id}/comments/
router.register('posts', PostViewSet, basename='posts')

router.register('reactions', ReactionViewSet, basename='reactions')

router.register('post_reactions', PostReactionViewSet, basename='post_reactions')

router.register('accounts', AccountViewSet, basename='accounts')

router.register('alumni_accounts', AlumniAccountViewSet, basename='alumni_accounts')

router.register('post_images', PostImageViewSet, basename='post_images')

router.register('comment', CommentViewSet, basename='comment')

router.register('invitation_groups', InvitationGroupViewSet, basename='invitation_groups')

router.register('post_invitations', PostInvitationViewSet, basename='post_invitations')

urlpatterns = [
    path('', include(router.urls)),
    path('send-email/', SendEmailView.as_view(), name='send-email'),
]
