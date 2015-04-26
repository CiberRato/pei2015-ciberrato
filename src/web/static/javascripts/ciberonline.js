(function (){
    'use strict';

    angular
        .module('ciberonline', [
            'ciberonline.config',
            'ciberonline.routes',
            'ciberonline.authentication',
            'ciberonline.profile',
            'ciberonline.teams',
            'ciberonline.search',
            'ciberonline.competitions',
            'ciberonline.agents',
            'ciberonline.rounds',
            'dndLists',
            'ciberonline.logviewer',
            'ciberonline.streamviewer',
            'ciberonline.grid',
            'SwampDragonServices'
        ])
        .run(run);

    angular
        .module('ciberonline.config', []);

    angular
        .module('ciberonline.routes', ['ngRoute']);

    run.$inject = ['$http', '$rootScope'];

    function run($http, $rootScope){
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
        $rootScope.$on("$routeChangeSuccess", function(event, currentRoute, previousRoute) {
            $rootScope.title = currentRoute.title;
        });
    }
})();