(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('CreateTeamController', CreateTeamController);

    CreateTeamController.$inject = ['$location', '$routeParams', 'Authentication', 'Team'];

    function CreateTeamController($location, $routeParams, Authentication, Team){
        var vm = this;

        vm.create = create;

        var username;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
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
                theme: 'success'
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
            $.jGrowl(errors, {
                life: 5000,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
            });
        }
    }
})();

