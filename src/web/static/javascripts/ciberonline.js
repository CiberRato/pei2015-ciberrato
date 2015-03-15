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
            'ciberonline.agents'
        ])
        .run(run);

    angular
        .module('ciberonline.config', []);

    angular
        .module('ciberonline.routes', ['ngRoute']);

    run.$inject = ['$http'];

    function run($http){
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }
})();