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
                $dragon.onReady(function() {
                    swampdragon.open(function () {
                       $dragon.onChannelMessage(function(channels, data) {
                            /*
                            if (data.data.message.status == 200){
                                $.jGrowl(data.data.message.content, {
                                    life: 3500,
                                    theme: 'success'
                                });
                            }else if(data.data.message.status == 400){
                                $.jGrowl(data.data.message.content, {
                                    life: 3500,
                                    theme: 'btn-danger'
                                });
                            }
                            */
                           if (data.data.message.trigger == ''){

                           }
                            console.log(channels);
                            console.log(data.data._type);
                            console.log(data.data.message);
                        });
                    });
                });
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
                $timeout(function(){
                   getAgents();
                });
            }

            function deleteAgentErrorFn(data){
                console.error(data.data);
                $.jGrowl("Agent could not be removed.", {
                    life: 2500,
                    theme: 'btn-danger'
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