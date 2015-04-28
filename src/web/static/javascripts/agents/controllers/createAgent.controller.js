(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('CreateAgentController', CreateAgentController);

    CreateAgentController.$inject = ['$location', '$timeout', 'Authentication', 'Agent', 'Team'];

    function CreateAgentController($location, $timeout, Authentication, Agent, Team){
        var vm = this;

        vm.create = create;

        vm.username;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            console.log(authenticatedAccount);
            vm.username = authenticatedAccount.username;

            Team.getUserAdmin(vm.username).then(getUserAdminSuccessFn, getUserAdminErrorFn);
            Agent.getLanguages().then(getLanguagesSuccessFn, getLanguagesErrorFn);

            function getUserAdminSuccessFn(data){
                vm.teams = data.data;
            }
            function getUserAdminErrorFn(data){
                console.error(data.data);
            }

            function getLanguagesSuccessFn(data){
                vm.languages = data.data;
            }

            function getLanguagesErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

        }

        function create(){
            var x;
            if(vm.teams.length > 0) {
                x = document.getElementById("select").value;
            }else {
                x = undefined;
            }
            var language = document.getElementById("selector_language").value;

            Agent.create(vm.name, x, language).then(createSuccessFn, createErrorFn);;
        }

        function createSuccessFn(){
            $.jGrowl("Agent has been created successfully.", {
                life: 2500,
                theme: 'success'
            });
            
            $location.path('/panel/'+ vm.username + '/myAgents/');

        }

        function createErrorFn(data){
            console.error(data.data.message);
            $.jGrowl("Error: Invalid name or an agent with that name already exists.", {
                life: 2500,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
            });
            $timeout(function(){
                activate();
            });
        }
    }
})();

