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
            'ciberonline.soloTrials',
            'angular-loading-bar',
            'cfp.loadingBar',
            'ngAnimate',
            'ciberonline.stickyNotes',
            'ciberonline.statistics',
            'ciberonline.hallOfFame',
            'ciberonline.notifications'
        ])
        .run(run);

    angular
        .module('ciberonline.config', ['angular-loading-bar']);

    angular
        .module('ciberonline.routes', ['ngRoute']);

    run.$inject = ['$http', '$rootScope', '$dragon', 'Authentication', 'Team', 'Notification'];

    function run($http, $rootScope, $dragon, Authentication, Team, Notification){
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
                });
                swampdragon.close(function () {
                    // Disable inputs depending on SwampDragon
                    console.log("foi-se a baixo!");
                });

                $dragon.onChannelMessage(function (channels, data) {
                    Notification.events.publish(data.data._type, data.data);
                });

                Notification.events.subscribe('notificationteam', function(data){
                    handle_messages(data);
                });

                Notification.events.subscribe('notificationuser', function(data){
                    handle_messages(data);
                });

                Notification.events.subscribe('notificationbroadcast', function(data){
                    handle_messages(data);
                });

                var handle_messages = function(data){
                    if (data.message.status == 200){
                        $.jGrowl(data.message.content, {
                            life: 3500,
                            theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                        });
                    }else if(data.message.status == 400){
                        $.jGrowl(data.message.content, {
                            life: 3500,
                            theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                        });
                    }else if(data.message.status == 100){
                        $.jGrowl(data.message.content, {
                            life: 3500,
                            theme: 'jGrowl-notification ui-state-highlight ui-corner-all info'
                        });
                    }
                }
            });
        }
    }
})();