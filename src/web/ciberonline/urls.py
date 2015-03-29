from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import TemplateView

from authentication.views import AccountViewSet, LoginView, LogoutView, AccountByFirstName, AccountByLastName

from groups.views import GroupMembersViewSet, AccountGroupsViewSet, GroupViewSet, MakeMemberAdminViewSet, \
    MemberInGroupViewSet, AccountGroupsAdminViewSet

from competition.views.group import EnrollGroup, CompetitionGetGroupsViewSet, CompetitionGetNotValidGroupsViewSet, \
    CompetitionOldestRoundViewSet, CompetitionEarliestRoundViewSet, MyEnrolledGroupsViewSet, ToggleGroupValid, \
    MyEnrolledGroupsInCompetitionViewSet, GetEnrolledGroupCompetitionsViewSet
from competition.views.cp_agent import AssociateAgent, AssociateAgentAdmin, AgentsAssociated
from competition.views.round import AgentsRound, RoundParticipants, RoundGroups, AgentsNotEligible, \
    RoundParticipantsNotEligible, RoundGroupsNotEligible, RoundViewSet, RoundViewAdminSet, RoundFile
from competition.views.simulation import SimulationViewSet, AssociateAgentToSimulation, \
    SimulationByAgent, SimulationByRound, SimulationByCompetition, GetSimulationAgents,  StartSimulation
from competition.views.view import CompetitionViewSet, CompetitionStateViewSet, CompetitionRounds, CompetitionChangeState
from competition.views.files import UploadParamListView, UploadGridView, UploadLabView, GetRoundFile

from simulations.views.all import SaveLogs, GetSimulation, GetSimulationLog

from agent.views.agent import AgentViewSets, AgentsByGroupViewSet, AgentsByUserViewSet
from agent.views.files import UploadAgent, DeleteUploadedFileAgent, GetAgentFilesSERVER, ListAgentsFiles, GetAllowedLanguages

from rest_framework import routers

router_accounts = routers.SimpleRouter()
router_accounts.register(r'accounts', AccountViewSet)
router_accounts.register(r'account_by_first_name', AccountByFirstName)
router_accounts.register(r'account_by_last_name', AccountByLastName)
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
router_competitions.register(r'get', CompetitionStateViewSet)
router_competitions.register(r'rounds', CompetitionRounds)
router_competitions.register(r'state', CompetitionChangeState)
# Groups
router_competitions.register(r'enroll', EnrollGroup)
router_competitions.register(r'groups', CompetitionGetGroupsViewSet)
router_competitions.register(r'groups_not_valid', CompetitionGetNotValidGroupsViewSet)
router_competitions.register(r'oldest_round', CompetitionOldestRoundViewSet)
router_competitions.register(r'earliest_round', CompetitionEarliestRoundViewSet)
router_competitions.register(r'my_enrolled_groups', MyEnrolledGroupsViewSet)
router_competitions.register(r'my_enrolled_groups_competition', MyEnrolledGroupsInCompetitionViewSet)
router_competitions.register(r'group_enrolled_competitions', GetEnrolledGroupCompetitionsViewSet)
router_competitions.register(r'toggle_group_inscription', ToggleGroupValid)
# Agent
router_competitions.register(r'associate_agent', AssociateAgent)
router_competitions.register(r'associate_agent_admin', AssociateAgentAdmin)
router_competitions.register(r'agents_by_competition_group', AgentsAssociated)
# Round
router_competitions.register(r'round', RoundViewSet)
router_competitions.register(r'round_admin', RoundViewAdminSet)
router_competitions.register(r'valid_round_agents', AgentsRound)
router_competitions.register(r'valid_round_participants', RoundParticipants)
router_competitions.register(r'valid_round_groups', RoundGroups)
router_competitions.register(r'not_eligible_round_agents', AgentsNotEligible)
router_competitions.register(r'not_eligible_round_participants', RoundParticipantsNotEligible)
router_competitions.register(r'not_eligible_round_groups', RoundGroupsNotEligible)
router_competitions.register(r'round_files', RoundFile)
# Simulation
router_competitions.register(r'simulation', SimulationViewSet)
router_competitions.register(r'associate_agent_to_simulation', AssociateAgentToSimulation)
router_competitions.register(r'simulations_by_agent', SimulationByAgent)
router_competitions.register(r'simulations_by_round', SimulationByRound)
router_competitions.register(r'simulations_by_competition', SimulationByCompetition)
router_competitions.register(r'simulation_agents', GetSimulationAgents)
# Simulation => Machine to Machine

# COMPETITIONS URLs#

# AGENTS URL's
router_agents = routers.SimpleRouter()
router_agents.register(r'agent', AgentViewSets)
router_agents.register(r'agents_by_group', AgentsByGroupViewSet)
router_agents.register(r'agents_by_user', AgentsByUserViewSet)
router_agents.register(r'delete_agent_file', DeleteUploadedFileAgent)
router_agents.register(r'agent_files', GetAgentFilesSERVER)

# SIMULATION URL's
router_simulations = routers.SimpleRouter()
router_simulations.register(r'simulation_log', SaveLogs)
router_simulations.register(r'get_simulation', GetSimulation)


urlpatterns = patterns('',
                       url(r'^api/v1/', include(router_accounts.urls)),
                       url(r'^api/v1/groups/', include(router_groups.urls)),
                       url(r'^api/v1/competitions/', include(router_competitions.urls)),
                       url(r'^api/v1/agents/', include(router_agents.urls)),
                       url(r'^api/v1/simulations/', include(router_simulations.urls)),

                       # upload files to round
                       url(r'^api/v1/competitions/round/upload/param_list/$', UploadParamListView.as_view(),
                           name="Param List Upload"),
                       url(r'^api/v1/competitions/round/upload/grid/$', UploadGridView.as_view(),
                           name="Grid Upload"),
                       url(r'^api/v1/competitions/round/upload/lab/$', UploadLabView.as_view(),
                           name="Lab Upload"),
                       # upload agent code
                       url(r'^api/v1/agents/upload/agent/$', UploadAgent.as_view(),
                           name="Lab Upload"),

                       # get allowed languags
                       url(r'^api/v1/agents/allowed_languages/$', GetAllowedLanguages.as_view(),
                           name="Allowed languages"),

                       # stat simulation
                       url(r'^api/v1/simulations/start/$', StartSimulation.as_view(), name="Start simulation"),
                       # get simulation log
                       url(r'^api/v1/simulations/get_simulation_log/(?P<simulation_id>.+)/$', GetSimulationLog.as_view(),
                           name="Get simulation log"),
                       # get round file
                       url(r'^api/v1/competitions/round_file/(?P<round_name>.+)/$', GetRoundFile.as_view(),
                           name="Get round file"),
                       # get agent files
                       url(r'^api/v1/agents/agent_file/(?P<simulation_id>.+)/(?P<agent_name>.+)/$',
                           ListAgentsFiles.as_view(),
                           name="Get agent files"),

                       # url(r'^api/v1/', include(router.urls)),
                       url(r"api/v1/auth/login/$", LoginView.as_view(), name="login"),
                       url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
                       url(r'^api-auth/', include('rest_framework.urls',
                                                  namespace='rest_framework')),
                       url('^admin/.*$', TemplateView.as_view(template_name='admin.html'), name='admin'),
                       url('^panel/.*$', TemplateView.as_view(template_name='panel.html'), name='panel'),
                       url('^idp/.*$', TemplateView.as_view(template_name='authentication.html'), name='idp'),
                       url('^.*$', TemplateView.as_view(template_name='index.html'), name='index')
)
urlpatterns[:0] = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
