(function(){

    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('DetailRoundController', DetailRoundController);

    DetailRoundController.$inject = ['$location', '$route', '$routeParams', 'Competition', 'Round', 'Authentication'];

    function DetailRoundController($location, $route, $routeParams, Competition, Round, Authentication){
        var vm = this;

        vm.createSimulation = createSimulation;
        vm.associateAgent = associateAgent;

        vm.roundName = $routeParams.name;
        activate();

        function activate() {
            Round.getSimulations(vm.roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);
            Round.getAgents(vm.roundName).then(getAgentsSuccessFn, getAgentsErrorFn);

            function getSimulationsSuccessFn(data){
                vm.simulations = data.data;
            }

            function getSimulationsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAgentsSuccessFn(data){
                vm.agents = data.data;
                console.log(vm.agents);
            }

            function getAgentsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

        }

        function createSimulation(){
            Round.createSimulation(vm.roundName).then(createSimulationSuccessFn, createSimulationErrorFn);

            function createSimulationSuccessFn(){
                $.jGrowl("Simulation has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function createSimulationErrorFn(data){
                console.error(data.data);
                $.jGrowl("Simulation has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }
        }

        function associateAgent(){
            var tdElem = document.getElementById ( "identifier" );
            var tdText = tdElem.innerHTML;
            var agent_name = document.getElementById("select").value;
            console.log(tdText);

            Round.getSimulationAgents(tdText).then(getSimulationAgentsSuccessFn, getSimulationAgentsErrorFn);

            function getSimulationAgentsSuccessFn(data) {
                vm.simulationAgents = data.data;
                vm.simulationAgents.count = vm.simulationAgents.length +1;

                console.log(vm.roundName + ' ' + tdText + ' ' + agent_name + ' ' + vm.simulationAgents.count);

                Round.associateAgent(vm.roundName, tdText, agent_name, vm.simulationAgents.count).then(associateAgentSuccessFn, associateAgentErrorFn);

                function associateAgentSuccessFn(){
                    $.jGrowl("Agent has been associated successfully.", {
                        life: 2500,
                        theme: 'success'
                    });
                    $route.reload();
                }

                function associateAgentErrorFn(data){
                    console.error(data.data);
                    $.jGrowl("Agent can't be associated.", {
                        life: 2500,
                        theme: 'success'
                    });
                    $route.reload();
                }
            }

            function getSimulationAgentsErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/');
            }



        }

    }

})();

