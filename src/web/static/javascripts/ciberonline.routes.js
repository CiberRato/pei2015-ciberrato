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
        }).when('/idp/login/',{
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: 'static/templates/authentication/login.html'
        }).when('/idp/panel/', {
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/profiles/profile.html'
        }).when('/',{
            templateUrl: '/templates/index.html'
        }).otherwise('/');
    }
})();