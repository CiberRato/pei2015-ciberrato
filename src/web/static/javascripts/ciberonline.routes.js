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
            templateUrl: '/static/templates/panel/changePassword.html'
        }).when('/panel/:username/editProfile',{
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/editProfile.html'
        }).when('/panel/:username/editProfile/deleteAccount',{
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/confirmAccount.html'
        }).when('/panel/:username/myTeams',{
            controller: 'MyTeamsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/myTeams.html'
        }).when('/panel/:username/createTeam',{
            controller: 'CreateTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/createTeam.html'
        }).when('/panel/:name/editTeam',{
            controller: 'TeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/editTeam.html'
        }).when('/panel/:name/editTeamProfile',{
            controller: 'EditTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/editTeamProfile.html'
        }).when('/panel/:name/editTeamProfile/deleteTeam',{
            controller: 'EditTeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/confirmTeam.html'
        }).when('/panel/:name/teamMembers',{
            controller: 'AllTeamsMembersController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/allTeamsMembers.html'
        }).when('/panel/:username/memberProfile',{
            controller: 'MemberProfile',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/memberProfile.html'
        }).when('/panel/allTeams',{
            controller:'AllTeamsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/allTeams.html'
        }).when('/panel/searchResults/:search',{
            controller:'SearchController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/search.html'
        }).when('/panel/competitions',{
            controller:'AllCompetitionsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/actualCompetitions.html'
        }).when('/',{
            templateUrl: '/templates/index.html'
        }).otherwise('/');
    }
})();