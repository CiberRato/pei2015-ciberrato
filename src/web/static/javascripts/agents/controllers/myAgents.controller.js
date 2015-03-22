(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('MyAgentsController', MyAgentsController);

    MyAgentsController.$inject = ['$location', '$route', 'Authentication', 'Agent', 'Team'];

    function MyAgentsController($location, $route, Authentication, Agent) {
        var vm = this;

        vm.deleteAgent = deleteAgent;

        activate();

        function activate() {
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            vm.username = authenticatedAccount.username;

            Agent.getByUser(vm.username).then(getByUserSuccessFn, getByUserErrorFn);

            function getByUserSuccessFn(data) {
                vm.agents = data.data;
            }

            function getByUserErrorFn(data) {
                console.error(data.data);
                $location.path("/panel/")
            }

        }

        function deleteAgent(agentName){
            Agent.deleteAgent(agentName).then(deleteAgentSuccessFn, deleteAgentErrorFn);

            function deleteAgentSuccessFn(){
                $.jGrowl("Agent has been removed successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload()
            }

            function deleteAgentErrorFn(data){
                console.error(data.data);
                $.jGrowl("Agent could not be removed.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }
    }
})();