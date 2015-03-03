from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import TemplateView

from authentication.views import AccountViewSet, LoginView, LogoutView

from groups.views import GroupMembersViewSet, AccountGroupsViewSet, GroupViewSet, MakeMemberAdminViewSet, \
    MemberInGroupViewSet
from competition.views import CompetitionViewSet, RoundViewSet, EnrollGroup
from competition.views import GetSimulation, UploadParamListView, UploadGridView, UploadLabView, \
    CompetitionGetGroupsViewSet, CompetitionEarliestRoundViewSet, CompetitionOldestRoundViewSet, \
    CompetitionGetNotValidGroupsViewSet, CompetitionGroupValidViewSet, AgentViewSets, UploadAgent, \
    DeleteUploadedFileAgent, AssociateAgent

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

# COMPETITIONS URLs#
router_competitions = routers.SimpleRouter()
router_competitions.register(r'crud', CompetitionViewSet)
router_competitions.register(r'round', RoundViewSet)
router_competitions.register(r'enroll', EnrollGroup)
router_competitions.register(r'groups', CompetitionGetGroupsViewSet)
router_competitions.register(r'groups_not_valid', CompetitionGetNotValidGroupsViewSet)
router_competitions.register(r'group_valid', CompetitionGroupValidViewSet)
router_competitions.register(r'oldest_round', CompetitionOldestRoundViewSet)
router_competitions.register(r'earliest_round', CompetitionEarliestRoundViewSet)
router_competitions.register(r'agent', AgentViewSets)
router_competitions.register(r'delete_agent_file', DeleteUploadedFileAgent)
router_competitions.register(r'associate_agent', AssociateAgent)

# COMPETITIONS URLs#

# melhorar isto
router_accounts.register(r'get_simulation', GetSimulation, 'Get simulation')

urlpatterns = patterns('',
                       url(r'^api/v1/', include(router_accounts.urls)),
                       url(r'^api/v1/groups/', include(router_groups.urls)),
                       url(r'^api/v1/competitions/', include(router_competitions.urls)),

                       # upload files to round
                       url(r'^api/v1/competitions/round/upload/param_list/$', UploadParamListView.as_view(),
                           name="Param List Upload"),
                       url(r'^api/v1/competitions/round/upload/grid/$', UploadGridView.as_view(),
                           name="Grid Upload"),
                       url(r'^api/v1/competitions/round/upload/lab/$', UploadLabView.as_view(),
                           name="Lab Upload"),
                       # upload agent code
                       url(r'^api/v1/competitions/upload/agent/$', UploadAgent.as_view(),
                           name="Lab Upload"),

                       # url(r'^api/v1/', include(router.urls)),
                       url(r"api/v1/auth/login/$", LoginView.as_view(), name="login"),
                       url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
                       url(r'^api-auth/', include('rest_framework.urls',
                                                  namespace='rest_framework')),
                       url('^panel/.*$', TemplateView.as_view(template_name='panel.html'), name='panel'),
                       url('^idp/.*$', TemplateView.as_view(template_name='authentication.html'), name='idp'),
                       url('^.*$', TemplateView.as_view(template_name='index.html'), name='index')
)
urlpatterns[:0] = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
