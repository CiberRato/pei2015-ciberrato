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
            controller: 'TeamController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/panel/editTeamProfile.html'
        }).when('/panel/allTeams',{
            controller:'AllTeamsController',
            controllerAs:'vm',
            templateUrl: '/static/templates/panel/allTeams.html'
        }).when('/',{
            templateUrl: '/templates/index.html'
        }).otherwise('/');
    }
})();