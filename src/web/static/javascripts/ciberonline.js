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
            'SwampDragonServices',
            'ui.ace',
            'ciberonline.users',
            'ciberonline.soloTrials'
        ])
        .run(run);

    angular
        .module('ciberonline.config', []);

    angular
        .module('ciberonline.routes', ['ngRoute']);

    run.$inject = ['$http', '$rootScope', '$dragon', 'Authentication', 'Team'];

    function run($http, $rootScope, $dragon, Authentication, Team){
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
        $rootScope.$on("$routeChangeSuccess", function(event, currentRoute, previousRoute) {
            $rootScope.title = currentRoute.title;
        });

        if (Authentication.isAuthenticated()) {
            console.log("AQUI");
            /* SUBSCRIBE */
            /// Subscribe to the chat router
            var user = Authentication.getAuthenticatedAccount();
            $dragon.onReady(function() {
                swampdragon.open(function () {
                    $dragon.subscribe('user', 'notifications', {'user': user}, function (context, data) {
                        // any thing that happens after successfully subscribing
                        console.log("// any thing that happens after successfully subscribing");
                    }, function (context, data) {
                        // any thing that happens if subscribing failed
                        console.log("// any thing that happens if subscribing failed");
                    });

                    var teams =[];
                    Team.getByUser(user.username).then(getTeamsSuccess, getTeamsError);

                    function getTeamsSuccess(data){
                        teams = data.data;
                        for(var i = 0; i<teams.length; i++){
                            $dragon.subscribe('team', 'notifications', {'user': user, 'team': teams[i].name}, function (context, data) {
                                // any thing that happens after successfully subscribing
                                console.log("// any thing that happens after successfully subscribing");
                            }, function (context, data) {
                                // any thing that happens if subscribing failed
                                console.log("// any thing that happens if subscribing failed");
                            });
                        }
                    }

                    function getTeamsError(data){
                        console.error(data.data);
                    }

                    $dragon.subscribe('broadcast', 'notifications', {'user': user}, function (context, data) {
                        // any thing that happens after successfully subscribing
                        console.log("// any thing that happens after successfully subscribing");
                    }, function (context, data) {
                        // any thing that happens if subscribing failed
                        console.log("// any thing that happens if subscribing failed");
                    });
                    $dragon.onChannelMessage(function(channels, data) {
                        if (data.data.message.status == 200){
                            $.jGrowl(data.data.message.content, {
                                life: 3500,
                                theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                            });
                        }else if(data.data.message.status == 400){
                            $.jGrowl(data.data.message.content, {
                                life: 3500,
                                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                            });
                        }else if(data.data.message.status == 100){
                            $.jGrowl(data.data.message.content, {
                                life: 3500,
                                theme: 'jGrowl-notification ui-state-highlight ui-corner-all info'
                            });
                        }
                        // console.log(channels);
                        console.log(data.data._type);
                        console.log(data.data.message);
                    });
                });
                swampdragon.close(function () {
                    // Disable inputs depending on SwampDragon
                    console.log("foi-se a baixo!");
                });
            });
        }
    }
})();