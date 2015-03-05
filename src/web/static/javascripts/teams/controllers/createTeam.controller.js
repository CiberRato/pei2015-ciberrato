(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('CreateTeamController', CreateTeamController);

    CreateTeamController.$inject = ['$location', '$routeParams', 'Authentication', 'Team'];

    function CreateTeamController($location, $routeParams, Authentication, Team){
        var vm = this;

        console.log("estive aqui");
        vm.create = create;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            var username = $routeParams.username;

            if(!authenticatedAccount){
                $location.url('/');
            }else{
                if(authenticatedAccount.username !== username){
                    $location.url('/');
                }
            }

        }

        function create(){
            Team.create(vm.name, vm.max_members);
        }
    }
})();

