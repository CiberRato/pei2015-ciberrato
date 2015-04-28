(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AllAgentController', AllAgentController);

    AllAgentController.$inject = ['$location', '$routeParams', 'Authentication', 'Agent', 'Team'];

    function AllAgentController($location, $routeParams, Authentication, Agent, Team){
        var vm = this;
        vm.destroyAgent = destroyAgent;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            var username = authenticatedAccount.username;
            vm.teamName = $routeParams.name;

            Agent.getByTeam(vm.teamName).then(getByTeamSuccessFn, getByTeamErrorFn);
            Team.getTeamInformation(vm.teamName, username).then(getTeamInfoSuccessFn, getTeamInfoErrorFn);

            function getByTeamSuccessFn(data){
                vm.agents = data.data;
            }

            function getByTeamErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getTeamInfoSuccessFn(data){
                vm.member = data;
            }
            function getTeamInfoErrorFn(data){
                console.error(data.data);
            }

        }

        function destroyAgent(agent){
            Agent.destroy(agent).then(destroyAgentSuccessFn, destroyAgentErrorFn);

            function destroyAgentSuccessFn(){
                $.jGrowl("Agent has been deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });

                $location.url('/panel/' + vm.teamName + '/allAgents');
            }

            function destroyAgentErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }
    }
})();
