(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$routeParams', 'Competition', 'Team', 'Agent'];

    function AgentDetailController($location, $routeParams, Competition, Team, Agent) {
        var vm = this;
        var agentName = $routeParams.name;

        activate();

        function activate() {
            Agent.getAgent(agentName).then(getAgentSuccessFn, getAgentErrorFn);

            function getAgentSuccessFn(data, status, headers, config) {
                vm.agent = data.data;
            }

            function getAgentErrorFn(data, status, headers, config) {
                console.error(data.data);
                $location.url('/panel/');
            }
        }
    }

})();
