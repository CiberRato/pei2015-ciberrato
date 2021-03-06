(function(){
    'use strict';

    angular
        .module('ciberonline.routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    function config($routeProvider){
        $routeProvider.when('/idp/register/',{
            controller: 'RegisterController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/register.html',
            title: 'Register'
        }).when('/idp/login',{
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: 'static/templates/authentication/login.html',
            title: 'Login'
        }).when('/idp/reset', {
            controller: 'ResetController',
            controllerAs: 'vm',
            templateUrl: 'static/templates/authentication/reset.html',
            title: 'Reset Password'
        }).when('/idp/recover/:token', {
            controller: 'RedefineController',
            controllerAs: 'vm',
            templateUrl: 'static/templates/authentication/redefine.html',
            title: 'Redefine Password'
        }).when('/panel/', {
            controller: 'PanelController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/index.html',
            title: 'Welcome!'
        }).when('/panel/:username/changePassword',{
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/profile/changePassword.html',
            title: 'Change Password'
        }).when('/panel/:username/editProfile',{
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/profile/editProfile.html',
            title: 'Edit Profile'
        }).when('/panel/:username/myTeams',{
            controller: 'MyTeamsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/myTeams.html',
            title: 'My Teams'
        }).when('/panel/:username/createTeam',{
            controller: 'CreateTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/createTeam.html',
            title: 'Create Team'
        }).when('/panel/:username/lastNotifications',{
            controller: 'LastNotificationsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/profile/lastNotifications.html',
            title: 'Last Notifications'
        }).when('/panel/:name/editTeam',{
            controller: 'TeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/editTeam.html',
            title: 'Edit Team'
        }).when('/panel/:name/editTeamProfile',{
            controller: 'EditTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/editTeamProfile.html',
            title: 'Edit Team Profile'
        }).when('/panel/:name/Scores',{
            controller:'ScoresController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/competition/competitionScores.html',
            title: 'Competition Score'
        }).when('/panel/:name/teamMembers',{
            controller: 'AllTeamsMembersController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/allTeamsMembers.html',
            title: 'Team Members'
        }).when('/panel/:username/memberProfile',{
            controller: 'MemberProfile',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/profile/memberProfile.html',
            title: 'Member Profile'
        }).when('/panel/allTeams',{
            controller:'AllTeamsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/teams/allTeams.html',
            title: 'All Teams'
        }).when('/panel/challenges',{
            controller:'AllChallengesController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/hallOfFame/allChallenges.html',
            title: 'Challenges'
        }).when('/panel/challenges/:name/scores',{
            controller:'ScoreChallengesController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/hallOfFame/scores.html',
            title: 'Challenges Scores'
        }).when('/panel/challenges/:name',{
            controller:'ChallengeDetailController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/hallOfFame/challengeDetail.html',
            title: 'Challenge Detail'
        }).when('/panel/searchResults/:search',{
            controller:'SearchController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/search.html',
            title: 'Search'
        }).when('/panel/competitions',{
            controller:'AllCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/actualCompetitions.html',
            title: 'Join Competitions'
        }).when('/panel/createAgent',{
            controller:'CreateAgentController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/agent/createAgent.html',
            title: 'Create Agent'
        }).when('/panel/pastCompetitions',{
            controller:'PastCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/pastCompetitions.html',
            title: 'Past Competitions'
        }).when('/panel/liveCompetitions',{
            controller:'LiveCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/liveCompetitions.html',
            title: 'Current Competitions'
        }).when('/panel/mySoloTrials',{
            controller:'SoloByUserController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/soloTrials/allSolos.html',
            title: 'My Solo Trials'
        }).when('/panel/trials/:identifier',{
            controller:'TrialsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/soloTrials/allTrials.html',
            title: 'My Solo Trials'
        }).when('/panel/myCompetitions/:username',{
            controller:'MyCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/myCompetitions.html',
            title: 'My Competitions'
        }).when('/panel/competitions/:name',{
            controller:'DetailCompetitionController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/competitionDetails.html',
            title: 'Competition Details'
        }).when('/panel/:name',{
            controller:'ListCompetitionController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/livePastCompetitions.html',
            title: 'Competitions'
        }).when('/panel/:username/myAgents',{
            controller:'MyAgentsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/agent/myAgents.html',
            title: 'My Agents'
        }).when('/panel/:teamName/:name/agentDetail/:fileName',{
            controller:'EditFileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/agent/fileEdit.html',
            title: 'Edit File'
        }).when('/panel/:teamName/:name/agentDetail',{
            controller:'AgentDetailController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/agent/agentDetail.html',
            title: 'Agent Details'
        }).when('/panel/:name/allAgents',{
            controller:'AllAgentController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/agent/allAgents.html',
            title: 'All Agents'
        }).when('/panel/:teamName/:identifier/createSoloTrial',{
            controller:'CreateSoloController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/soloTrials/createSolo.html',
            title: 'Solo Trials'
        }).when('/panel/:teamName/:identifier/soloTrials',{
            controller:'SoloByTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/soloTrials/soloByTeam.html',
            title: 'Solo Trials'
        }).when('/admin/',{
            templateUrl: '/static/templates/admin/index.html',
            title: 'Welcome!'
        }).when('/admin/:name/Scores',{
            controller:'ScoresController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/competition/competitionScores.html',
            title: 'Competition Score'
        }).when('/admin/allCompetitions',{
            controller:'AllTogetherCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/admin/competition/allCompetitions.html',
            title: 'All Competitions'
        }).when('/admin/createCompetition',{
            controller:'CreateCompetitionController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/competition/createCompetition.html',
            title: 'Create Competition'
        }).when('/admin/allUsers',{
            controller:'ChangePermissionsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/user/changePermissions.html',
            title: 'All Users'
        }).when('/admin/createTypeOfCompetition',{
            controller:'CreateTypeOfCompetitionController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/competition/createType.html',
            title: 'Create Type Of Competition'
        }).when('/admin/allTypesOfCompetition',{
            controller:'AllTypesOfCompetitionController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/competition/allTypes.html',
            title: 'Types of Competitions'
        }).when('/admin/editTypeOfCompetition/:name',{
            controller:'EditTypeOfCompetitionController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/competition/editType.html',
            title: 'Edit Type of Competition'
        }).when('/admin/createStickyNote',{
            controller:'CreateStickyNotesController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/stickyNotes/createStickyNote.html',
            title: 'Create Sticky Notes'
        }).when('/admin/challenges',{
            controller:'AllChallengesController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/hallOfFame/allChallenges.html',
            title: 'Challenges'
        }).when('/admin/createChallenge',{
            controller:'CreateChallengeController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/hallOfFame/createChallenge.html',
            title: 'Create Challenge'
        }).when('/admin/:competitionName/:roundName/editMap/',{
            controller:'EditMapController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/round/editMap.html',
            title: 'Create Challenge'
        }).when('/admin/statistics',{
            controller:'StatisticsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/statistics/statistics.html',
            title: 'Statistics'
        }).when('/admin/stickyNotes',{
            controller:'AllStickyNotesController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/stickyNotes/stickyNotes.html',
            title: 'Sticky Notes'
        }).when('/admin/:name/',{
            controller:'ListCompetitionController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/competition/livePastCompetitions.html',
            title: 'Past Competitions'
        }).when('/admin/:competitionName/:name/roundDetail',{
            controller:'DetailRoundController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/round/roundDetail.html',
            title: 'Round Details'
        }).when('/admin/:name/createRound',{
            controller:'CreateRoundController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/admin/round/newRound.html',
            title: 'Create Round'
        }).when('/panel/:identifier/watchTrial',{
            templateUrl: '/static/templates/viewer/logViewer.html',
            title: 'Watch Trial'
        }).when('/panel/:identifier/liveStream',{
            templateUrl: '/static/templates/viewer/streamViewer.html',
            title: 'Live Stream'
        }).when('/panel/apps/desktopSoftware',{
            templateUrl: '/static/templates/panel/desktopSoftware.html',
            title: 'Desktop Software'
        }).when('/panel/team/credits',{
            templateUrl: '/static/templates/panel/credits.html',
            title: 'Credits'
        }).when('/panel/api/documentation',{
            templateUrl: '/static/templates/panel/api_documentation.html',
            title: 'API Documentation'
        }).when('/' ,{
            templateUrl: '/templates/index.html'
        }).otherwise('/');
    }
})();