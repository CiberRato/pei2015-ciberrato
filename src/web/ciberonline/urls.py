from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from authentication.views import AccountViewSet, LoginView, LogoutView, AccountByFirstName, AccountByLastName, \
    AccountChangePassword, ToggleUserToStaff, ToggleUserToSuperUser, LoginToOtherUser, MyDetails

from teams.views import TeamMembersViewSet, AccountTeamsViewSet, TeamViewSet, MakeMemberAdminViewSet, \
    MemberInTeamViewSet, AccountTeamsAdminViewSet

from competition.views.team import EnrollTeam, CompetitionGetTeamsViewSet, CompetitionGetNotValidTeamsViewSet, \
    CompetitionOldestRoundViewSet, CompetitionEarliestRoundViewSet, MyEnrolledTeamsViewSet, ToggleTeamValid, \
    MyEnrolledTeamsInCompetitionViewSet, GetEnrolledTeamCompetitionsViewSet, AdminEnrollTeam
from competition.views.round import RoundTeams, RoundViewSet, RoundFile, GetResourcesFiles

from competition.views.trial import TrialViewSet, TrialByAgent, TrialByRound, \
    TrialByCompetition, GetTrialAgents, StartTrial, TrialGridViewSet, PrepareTrial
from competition.views.view import CompetitionViewSet, CompetitionStateViewSet, CompetitionRounds, \
    CompetitionChangeState, TypeOfCompetitionViewSet
from competition.views.files import UploadParamListView, UploadGridView, UploadLabView, GetRoundFile, \
    UploadResourceFile
from competition.views.grid_position import GridPositionsViewSet, AgentGridViewSet, GridPositionsByCompetition
from competition.views.teamscore import TeamScoreViewSet, RankingByTrial, RankingByRound, RankingByCompetition, \
    RankingByTeamInCompetition

from competition.views.trials import SaveLogs, GetTrial, GetTrialLog, SaveSimErrors, TrialMessageCreate

from competition.views.private_competitions import PrivateCompetitionsUser, PrivateCompetitionsRounds, \
    CreatePrivateCompetitionRound, GetRoundTrials, RunPrivateTrial

from agent.views.agent import AgentViewSets, AgentsByTeamViewSet, AgentsByUserViewSet, AgentCodeValidation, \
    SubmitCodeForValidation, AgentsByTeamValidViewSet
from agent.views.files import UploadAgent, DeleteUploadedFileAgent, GetAgentFilesSERVER, ListAgentsFiles, \
    GetAllowedLanguages, GetAllAgentFiles, GetAgentFile

from rest_framework import routers


router_accounts = routers.SimpleRouter()
router_accounts.register(r'accounts', AccountViewSet)
router_accounts.register(r'change_password', AccountChangePassword)
router_accounts.register(r'account_by_first_name', AccountByFirstName)
router_accounts.register(r'account_by_last_name', AccountByLastName)
router_accounts.register(r'toggle_staff', ToggleUserToStaff)
router_accounts.register(r'toggle_super_user', ToggleUserToSuperUser)
router_accounts.register(r'login_to', LoginToOtherUser)
# GROUPS URLs
router_teams = routers.SimpleRouter()
router_teams.register(r'members', TeamMembersViewSet)
router_teams.register(r'user', AccountTeamsViewSet)
router_teams.register(r'user_admin', AccountTeamsAdminViewSet)
# crud = create read update delete
router_teams.register(r'crud', TeamViewSet)
router_teams.register(r'admin', MakeMemberAdminViewSet)
router_teams.register(r'member', MemberInTeamViewSet)
# GROUPS URLs

# COMPETITIONS URLs#
router_competitions = routers.SimpleRouter()
router_competitions.register(r'crud', CompetitionViewSet)
router_competitions.register(r'get', CompetitionStateViewSet)
router_competitions.register(r'rounds', CompetitionRounds)
router_competitions.register(r'state', CompetitionChangeState)
router_competitions.register(r'type_of_competition', TypeOfCompetitionViewSet)
router_competitions.register(r'grid_position', GridPositionsViewSet)
router_competitions.register(r'grid_positions_competition', GridPositionsByCompetition)
router_competitions.register(r'agent_grid', AgentGridViewSet)
router_competitions.register(r'team_score', TeamScoreViewSet)
router_competitions.register(r'ranking_trial', RankingByTrial)
router_competitions.register(r'ranking_round', RankingByRound)
router_competitions.register(r'ranking_competition', RankingByCompetition)
router_competitions.register(r'ranking_team_competition', RankingByTeamInCompetition)
# Teams
router_competitions.register(r'enroll', EnrollTeam)
router_competitions.register(r'teams', CompetitionGetTeamsViewSet)
router_competitions.register(r'teams_not_valid', CompetitionGetNotValidTeamsViewSet)
router_competitions.register(r'oldest_round', CompetitionOldestRoundViewSet)
router_competitions.register(r'earliest_round', CompetitionEarliestRoundViewSet)
router_competitions.register(r'my_enrolled_teams', MyEnrolledTeamsViewSet)
router_competitions.register(r'my_enrolled_teams_competition', MyEnrolledTeamsInCompetitionViewSet)
router_competitions.register(r'team_enrolled_competitions', GetEnrolledTeamCompetitionsViewSet)
router_competitions.register(r'toggle_team_inscription', ToggleTeamValid)
router_competitions.register(r'remove_enroll_team', AdminEnrollTeam)
# Round
router_competitions.register(r'round', RoundViewSet)
router_competitions.register(r'round_teams', RoundTeams)
router_competitions.register(r'round_files', RoundFile)
# Trial
router_competitions.register(r'trial', TrialViewSet)
router_competitions.register(r'trials_by_agent', TrialByAgent)
router_competitions.register(r'trials_by_round', TrialByRound)
router_competitions.register(r'trials_by_competition', TrialByCompetition)
router_competitions.register(r'trial_agents', GetTrialAgents)
router_competitions.register(r'trial_grid', TrialGridViewSet)
# Trial => Machine to Machine

# COMPETITIONS URLs#

# AGENTS URL's
router_agents = routers.SimpleRouter()
router_agents.register(r'agent', AgentViewSets)
router_agents.register(r'agents_by_team', AgentsByTeamViewSet)
router_agents.register(r'agents_valid_by_team', AgentsByTeamValidViewSet)
router_agents.register(r'agents_by_user', AgentsByUserViewSet)
router_agents.register(r'delete_agent_file', DeleteUploadedFileAgent)
router_agents.register(r'agent_files', ListAgentsFiles)
router_agents.register(r'code_validation', AgentCodeValidation)
router_agents.register(r'validate_code', SubmitCodeForValidation)

# TRIAL URL's
router_trials = routers.SimpleRouter()
router_trials.register(r'trial_log', SaveLogs)
router_trials.register(r'trial_error', SaveSimErrors)
router_trials.register(r'get_trial', GetTrial)
router_trials.register(r'prepare', PrepareTrial)

# Private Competitions
router_private_competitions = routers.SimpleRouter()
router_private_competitions.register(r'list', PrivateCompetitionsUser)
router_private_competitions.register(r'rounds', PrivateCompetitionsRounds)
router_private_competitions.register(r'create_round', CreatePrivateCompetitionRound)
router_private_competitions.register(r'round', GetRoundTrials)


urlpatterns = patterns('',
                       url(r'^api/v1/', include(router_accounts.urls)),
                       url(r'^api/v1/me/$', MyDetails.as_view(), name="ME"),
                       url(r'^api/v1/teams/', include(router_teams.urls)),
                       url(r'^api/v1/competitions/', include(router_competitions.urls)),
                       url(r'^api/v1/competitions/private/', include(router_private_competitions.urls)),
                       url(r'^api/v1/competitions/private/launch_trial/$', RunPrivateTrial.as_view(),
                           name="Launch private trial"),

                       url(r'^api/v1/agents/', include(router_agents.urls)),
                       url(r'^api/v1/trials/', include(router_trials.urls)),
                       url(r'^api/v1/trials/message/$', TrialMessageCreate.as_view(),
                           name="Trial message Upload"),

                       # upload files to round
                       url(r'^api/v1/competitions/round/upload/param_list/$', UploadParamListView.as_view(),
                           name="Param List Upload"),
                       url(r'^api/v1/competitions/round/upload/grid/$', UploadGridView.as_view(),
                           name="Grid Upload"),
                       url(r'^api/v1/competitions/round/upload/lab/$', UploadLabView.as_view(),
                           name="Lab Upload"),
                       # upload agent code

                       url(r'^api/v1/round_resources/$', GetResourcesFiles.as_view(),
                           name="Resources"),

                       url(r'^api/v1/agents/upload/agent/$', UploadAgent.as_view(),
                           name="Lab Upload"),

                       # get allowed languags
                       url(r'^api/v1/agents/allowed_languages/$', GetAllowedLanguages.as_view(),
                           name="Allowed languages"),

                       # stat trial
                       url(r'^api/v1/trials/start/$', StartTrial.as_view(), name="Start trial"),
                       # get trial log
                       url(r'^api/v1/trials/get_trial_log/(?P<trial_id>.+)/$',
                           GetTrialLog.as_view(),
                           name="Get trial log"),
                       # get round file
                       url(r'^api/v1/competitions/round_file/(?P<competition_name>.+)/(?P<round_name>.+)/(?P<param>.+)/$',
                           GetRoundFile.as_view(),
                           name="Get round file"),
                       # set round file
                       url(r'^api/v1/set_round_file/(?P<round_name>.+)/(?P<param>.+)/$',
                           UploadResourceFile.as_view(), name="Set round file"),

                       # get agent files
                       url(r'^api/v1/agents/agent_file/(?P<team_name>.+)/(?P<agent_name>.+)/$',
                           GetAgentFilesSERVER.as_view(),
                           name="Get agent files SERVER"),

                       # get agent file
                       url(r'^api/v1/agents/file/(?P<team_name>.+)/(?P<agent_name>.+)/(?P<file_name>.+)/$',
                           GetAgentFile.as_view(),
                           name="Get agent files SERVER"),

                       # get all agent files
                       url(r'^api/v1/agents/agent_all_files/(?P<team_name>.+)/(?P<agent_name>.+)/$',
                           GetAllAgentFiles.as_view(),
                           name="Get all agent files"),

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
# urlpatterns[:0] = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)