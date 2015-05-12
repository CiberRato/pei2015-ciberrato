(function(){
    'use strict';

    angular
        .module('ciberonline.config')
        .config(config);

    config.$inject = ['$locationProvider', 'cfpLoadingBarProvider'];

    function config($locationProvider, cfpLoadingBarProvider){
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');
        cfpLoadingBarProvider.latencyThreshold = 50;

    }
})();