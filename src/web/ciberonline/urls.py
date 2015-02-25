from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from authentication.views import AccountViewSet, LoginView, LogoutView

from groups.views import GroupMembersViewSet, AccountGroupsViewSet, GroupViewSet, MakeMemberAdminViewSet, MemberInGroupViewSet
from competition.views import GetSimulation

from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)

# GROUPS URSL
router.register(r'group_members', GroupMembersViewSet)
router.register(r'user_groups', AccountGroupsViewSet)
router.register(r'group', GroupViewSet)
router.register(r'make_group_admin', MakeMemberAdminViewSet)
router.register(r'group_member', MemberInGroupViewSet)
# GROUPS URSL

router.register(r'get_simulation', GetSimulation, 'Get simulation')

urlpatterns = patterns('',
    url(r'^api/v1/', include(router.urls)),
    url(r"api/v1/auth/login/$", LoginView.as_view(), name="login"),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
