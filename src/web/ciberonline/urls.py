from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from authentication.views import AccountViewSet, LoginView, LogoutView

from groups.views import GroupMembersViewSet, AccountGroupsViewSet, GroupViewSet, MakeMemberAdminViewSet, MemberInGroupViewSet
from competition.views import GetSimulation

from rest_framework import routers

router_accounts = routers.SimpleRouter()
router_accounts.register(r'accounts', AccountViewSet)

# GROUPS URLs
router_groups = routers.SimpleRouter()
router_groups.register(r'members', GroupMembersViewSet)
router_groups.register(r'user', AccountGroupsViewSet)
# crud = create read update delete
router_groups.register(r'crud', GroupViewSet)
router_groups.register(r'admin', MakeMemberAdminViewSet)
router_groups.register(r'member', MemberInGroupViewSet)
# GROUPS URLs

#router.register(r'get_simulation', GetSimulation, 'Get simulation')

urlpatterns = patterns('',
    url(r'^api/v1/', include(router_accounts.urls)),
    url(r'^api/v1/groups/', include(router_groups.urls)),
    #url(r'^api/v1/', include(router.urls)),
    url(r"api/v1/auth/login/$", LoginView.as_view(), name="login"),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
