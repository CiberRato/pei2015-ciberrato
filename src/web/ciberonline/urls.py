from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import TemplateView

from authentication.views import AccountViewSet, LoginView, LogoutView

from groups.views import GroupMembersViewSet, AccountGroupsViewSet, GroupViewSet, MakeMemberAdminViewSet, \
    MemberInGroupViewSet, AccountGroupsAdminViewSet
from competition.views.group import EnrollGroup, CompetitionGetGroupsViewSet, CompetitionGetNotValidGroupsViewSet, \
    CompetitionGroupValidViewSet, CompetitionOldestRoundViewSet, CompetitionEarliestRoundViewSet
from competition.views.agent import AssociateAgent, AgentViewSets
from competition.views.round import AgentsRound, RoundParticipants, RoundGroups, AgentsNotEligible, \
    RoundParticipantsNotEligible, RoundGroupsNotEligible, RoundViewSet
from competition.views.simulation import SimulationViewSet, AssociateAgentToSimulation, \
    SimulationByAgent, SimulationByRound, SimulationByCompetition, GetSimulations, GetSimulationAgents, SaveLogs
from competition.views.view import CompetitionViewSet
from competition.views.files import UploadParamListView, UploadGridView, UploadLabView, UploadAgent, \
    DeleteUploadedFileAgent, GetRoundFile, GetAgentFiles

from rest_framework import routers

router_accounts = routers.SimpleRouter()
router_accounts.register(r'accounts', AccountViewSet)

# GROUPS URLs
router_groups = routers.SimpleRouter()
router_groups.register(r'members', GroupMembersViewSet)
router_groups.register(r'user', AccountGroupsViewSet)
router_groups.register(r'user_admin', AccountGroupsAdminViewSet)
# crud = create read update delete
router_groups.register(r'crud', GroupViewSet)
router_groups.register(r'admin', MakeMemberAdminViewSet)
router_groups.register(r'member', MemberInGroupViewSet)
# GROUPS URLs

# COMPETITIONS URLs#
router_competitions = routers.SimpleRouter()
router_competitions.register(r'crud', CompetitionViewSet)
# Groups
router_competitions.register(r'enroll', EnrollGroup)
router_competitions.register(r'groups', CompetitionGetGroupsViewSet)
router_competitions.register(r'groups_not_valid', CompetitionGetNotValidGroupsViewSet)
router_competitions.register(r'group_valid', CompetitionGroupValidViewSet)
router_competitions.register(r'oldest_round', CompetitionOldestRoundViewSet)
router_competitions.register(r'earliest_round', CompetitionEarliestRoundViewSet)
# Agent
router_competitions.register(r'agent', AgentViewSets)
router_competitions.register(r'associate_agent', AssociateAgent)
# Round
router_competitions.register(r'round', RoundViewSet)
router_competitions.register(r'valid_round_agents', AgentsRound)
router_competitions.register(r'valid_round_participants', RoundParticipants)
router_competitions.register(r'valid_round_groups', RoundGroups)
router_competitions.register(r'not_eligible_round_agents', AgentsNotEligible)
router_competitions.register(r'not_eligible_round_participants', RoundParticipantsNotEligible)
router_competitions.register(r'not_eligible_round_groups', RoundGroupsNotEligible)
# Simulation
router_competitions.register(r'simulation', SimulationViewSet)
router_competitions.register(r'associate_agent_to_simulation', AssociateAgentToSimulation)
router_competitions.register(r'simulations_by_agent', SimulationByAgent)
router_competitions.register(r'simulations_by_round', SimulationByRound)
router_competitions.register(r'simulations_by_competition', SimulationByCompetition)
router_competitions.register(r'simulation_agents', GetSimulationAgents)
router_competitions.register(r'simulation_log', SaveLogs)
router_competitions.register(r'get_simulations', GetSimulations)
# Uploads
router_competitions.register(r'delete_agent_file', DeleteUploadedFileAgent)

# COMPETITIONS URLs#

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

                       # get round file
                       url(r'^api/v1/competitions/round_file/(?P<round_name>.+)/$', GetRoundFile.as_view(),
                           name="Get round file"),
                       # get agent files
                       url(r'^api/v1/competitions/agent_file/(?P<simulation_id>.+)/(?P<agent_name>.+)/$',
                           GetAgentFiles.as_view(),
                           name="Get agent files"),

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
