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
            $.jGrowl("Team has been created successfully.", {
                life: 2500,
                theme: 'success'
            });
            $location.path('/panel/'+ username + '/myTeams/');

        }

        function createErrorFn(data){
            console.error(data.data);
            $.jGrowl("Team could not be created.", {
                life: 2500,
                theme: 'btn-danger'
            });
        }
    }
})();

