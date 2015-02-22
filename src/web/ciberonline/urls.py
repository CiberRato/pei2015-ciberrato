from django.conf.urls import patterns, include, url
from django.contrib import admin

from authentication.views import AccountViewSet, LoginView, LogoutView

from groups.views import GroupMembersViewSet, AccountGroupsViewSet, GroupViewSet, MakeMemberAdminViewSet, MemberInGroupViewSet

from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)

router.register(r'group_members', GroupMembersViewSet)
router.register(r'user_groups', AccountGroupsViewSet)
router.register(r'group', GroupViewSet)
router.register(r'make_group_admin', MakeMemberAdminViewSet)
router.register(r'group_member', MemberInGroupViewSet)

account_router = routers.NestedSimpleRouter(
    router, r'accounts', lookup='account'
)
urlpatterns = patterns('',
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include(account_router.urls)),
    url(r"api/v1/auth/login/$", LoginView.as_view(), name="login"),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)
