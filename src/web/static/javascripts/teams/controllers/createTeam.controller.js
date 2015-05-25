(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('CreateTeamController', CreateTeamController);

    CreateTeamController.$inject = ['$location', '$routeParams', '$dragon', 'Authentication', 'Team'];

    function CreateTeamController($location, $routeParams, $dragon, Authentication, Team){
        var vm = this;

        vm.create = create;

        var username;
        var authenticatedAccount;

        activate();

        function activate(){

            authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = $routeParams.username;

            if(!authenticatedAccount){
                $location.url('/');
            }else{
                if(authenticatedAccount.username !== username){
                    $location.url('/');
                }
            }

        }

        function create(){
            Team.create(vm.name, vm.max_members).then(createSuccessFn, createErrorFn);;
        }

        function createSuccessFn(){
            $.jGrowl("Team successfully created.", {
                life: 2500,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
            });
            $dragon.onReady(function() {
                swampdragon.open(function () {
                    $dragon.subscribe('team', 'notifications', {
                        'user': authenticatedAccount,
                        'team': vm.name
                    }, function (context, data) {
                        // any thing that happens after successfully subscribing
                        console.log("// any thing that happens after successfully subscribing");
                    }, function (context, data) {
                        // any thing that happens if subscribing failed
                        console.log("// any thing that happens if subscribing failed");
                    });
                });
            });
            $location.path('/panel/'+ username + '/myTeams/');

        }

        function createErrorFn(data){
            console.error(data.data);
            var errors = "";
            for (var value in data.data.message) {
                errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                for (var error in data.data.message[value]){
                    errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                }
            }
            if(typeof data.data.detail !== 'undefined'){
                errors += " &nbsp; "+ data.data.detail + '<br/>';
            }
            $.jGrowl(errors, {
                life: 5000,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
            });
        }
    }
})();

