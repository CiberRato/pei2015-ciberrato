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
            templateUrl: '/static/templates/authentication/register.html'
        }).when('/idp/login',{
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: 'static/templates/authentication/login.html'
        }).when('/panel/', {
            templateUrl: '/static/templates/panel/index.html'
        }).when('/panel/:username/changePassword',{
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/profile/changePassword.html'
        }).when('/panel/:username/editProfile',{
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/profile/editProfile.html'
        }).when('/panel/:username/myTeams',{
            controller: 'MyTeamsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/myTeams.html'
        }).when('/panel/:username/createTeam',{
            controller: 'CreateTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/createTeam.html'
        }).when('/panel/:name/editTeam',{
            controller: 'TeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/editTeam.html'
        }).when('/panel/:name/editTeamProfile',{
            controller: 'EditTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/editTeamProfile.html'
        }).when('/panel/:name/teamMembers',{
            controller: 'AllTeamsMembersController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/teams/allTeamsMembers.html'
        }).when('/panel/:username/memberProfile',{
            controller: 'MemberProfile',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/profile/memberProfile.html'
        }).when('/panel/allTeams',{
            controller:'AllTeamsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/teams/allTeams.html'
        }).when('/panel/searchResults/:search',{
            controller:'SearchController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/search.html'
        }).when('/panel/competitions',{
            controller:'AllCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/actualCompetitions.html'
        }).when('/panel/allCompetitions',{
            controller:'AllTogetherCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/allCompetitions.html'
        }).when('/panel/pastCompetitions',{
            controller:'PastCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/pastCompetitions.html'
        }).when('/panel/liveCompetitions',{
            controller:'LiveCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/liveCompetitions.html'
        }).when('/panel/myCompetitions/:username',{
            controller:'MyCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/myCompetitions.html'
        }).when('/panel/competitions/:name',{
            controller:'DetailCompetitionController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/competition/competitionDetails.html'
        }).when('/panel/createAgent',{
            controller:'CreateAgentController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/agent/createAgent.html'
        }).when('/panel/:username/myAgents',{
            controller:'MyAgentsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/agent/myAgents.html'
        }).when('/panel/:name/agentDetail',{
            controller:'AgentDetailController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/agent/agentDetail.html'
        }).when('/panel/:name/allAgents',{
            controller:'AllAgentController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/agent/allAgents.html'
        }).when('/' ,{
            templateUrl: '/templates/index.html'
        }).otherwise('/');
    }
})();