(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('MyAgentsController', MyAgentsController);

    MyAgentsController.$inject = ['$location', '$timeout', '$dragon', 'Authentication', 'Agent', 'Team'];

    function MyAgentsController($location, $timeout, $dragon, Authentication, Agent) {
        var vm = this;

        vm.deleteAgent = deleteAgent;

        activate();

        function activate() {
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            vm.username = authenticatedAccount.username;

            Agent.getByUser(vm.username).then(getByUserSuccessFn, getByUserErrorFn);

            function getByUserSuccessFn(data) {
                vm.agents = data.data;
                console.log(vm.agents);

            }

            function getByUserErrorFn(data) {
                console.error(data.data);
                $location.path("/panel/")
            }

        }

        function deleteAgent(agentName, teamName){
            Agent.deleteAgent(agentName, teamName).then(deleteAgentSuccessFn, deleteAgentErrorFn);

            function deleteAgentSuccessFn(){
                $.jGrowl("Agent has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                   getAgents();
                });
            }

            function deleteAgentErrorFn(data){
                console.error(data.data);
                $.jGrowl("Agent could not be removed.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function getAgents(){
            Agent.getByUser(vm.username).then(getByUserSuccessFn, getByUserErrorFn);

            function getByUserSuccessFn(data) {
                vm.agents = data.data;
                console.log(vm.agents);
            }

            function getByUserErrorFn(data) {
                console.error(data.data);
                $location.path("/panel/")
            }
        }

    }
})();