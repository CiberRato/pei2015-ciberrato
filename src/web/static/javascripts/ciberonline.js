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

    run.$inject = ['$http', '$rootScope', '$dragon', 'Authentication'];

    function run($http, $rootScope, $dragon, Authentication){
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
        $rootScope.$on("$routeChangeSuccess", function(event, currentRoute, previousRoute) {
            $rootScope.title = currentRoute.title;
        });

        if (Authentication.isAuthenticated()) {
            console.log("AQUI");
            /* SUBSCRIBE */
            /// Subscribe to the chat router
            $dragon.onReady(function() {
                $dragon.subscribe('notifications', 'notifications', {'user': Authentication.getAuthenticatedAccount()}, function (context, data) {
                    // any thing that happens after successfully subscribing
                    console.log("// any thing that happens after successfully subscribing");
                }, function (context, data) {
                    // any thing that happens if subscribing failed
                    console.log("// any thing that happens if subscribing failed");
                });
            });

            $dragon.onChannelMessage(function(channels, data) {
                console.log(data.data.message);
            });
        }
    }
})();