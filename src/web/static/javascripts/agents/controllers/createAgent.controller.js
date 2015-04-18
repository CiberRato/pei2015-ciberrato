(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('CreateAgentController', CreateAgentController);

    CreateAgentController.$inject = ['$location', '$route', 'Authentication', 'Agent', 'Team'];

    function CreateAgentController($location, $route, Authentication, Agent, Team){
        var vm = this;

        vm.create = create;

        var username;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;

            Team.getUserAdmin(username).then(getUserAdminSuccessFn, getUserAdminErrorFn);

            function getUserAdminSuccessFn(data){
                vm.teams = data.data;
            }
            function getUserAdminErrorFn(data){
                console.error(data.data);
            }

        }

        function create(){
            var x = document.getElementById("select").value;
            var y = document.getElementById("type").value;
            Agent.create(vm.name, x, y).then(createSuccessFn, createErrorFn);;
        }

        function createSuccessFn(){
            $.jGrowl("Agent has been created successfully.", {
                life: 2500,
                theme: 'success'
            });
            $location.path('/panel/'+ username + '/myAgents/');

        }

        function createErrorFn(data){
            console.error(data.data.message);
            $.jGrowl("Error: Invalid name or an agent with that name already exists.", {
                life: 2500,
                theme: 'btn-danger'
            });
            $route.reload();
        }
    }
})();

