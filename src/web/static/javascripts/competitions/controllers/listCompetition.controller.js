(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ListCompetitionController', ListCompetitionController);

    ListCompetitionController.$inject = ['$location', '$route', '$routeParams', 'Competition', 'Round'];

    function ListCompetitionController($location, $route, $routeParams, Competition, Round){
        var vm = this;
        vm.competitionName = $routeParams.name;
        vm.startSimulation = startSimulation;

        activate();

        function activate() {
            Competition.getCompetition(vm.competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);
            Competition.getAllRounds(vm.competitionName).then(getAllRoundsSuccessFn, getAllRoundsErrorFn);

            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
                Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                function getTeamsSuccessFn(data, status, headers, config) {
                    vm.competitionTeamsInfo = data.data;
                    for (var l = 0; l < vm.competitionTeamsInfo.length; l++) {
                        getAgents(vm.competitionTeamsInfo[l].group.name, l);

                    }
                    function getAgents(name, l) {
                        Competition.agents(name, vm.competitionName).then(agentsSuccessFn, agentsErrorFn);

                        function agentsSuccessFn(data) {
                            vm.competitionTeamsInfo[l].agents = data.data;
                            console.log(vm.competitionTeamsInfo[l].agents.length);
                        }

                        function agentsErrorFn(data, status, headers, config) {
                            console.error(data.data);
                            $location.url('/panel/');
                        }
                    }
                }

                function getTeamsErrorFn(data, status, headers, config) {
                    console.error(data.data);
                    $location.url('/panel/');
                }
            }

            function getCompetitionErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAllRoundsSuccessFn(data){
                vm.rounds = data.data;
                for(var i = 0; i<vm.rounds.length; i++){
                    getSimulations(vm.rounds[i].name, i);
                }
            }

            function getSimulations(roundName, i){
                Round.getSimulations(roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);

                function getSimulationsSuccessFn(data){
                    vm.rounds[i].simulations = data.data;
                }

                function getSimulationsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');

                }
            }

            function getAllRoundsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function startSimulation(identifier){
            console.log(identifier);
            Round.startSimulation(identifier).then(startSimulationSuccessFn, startSimulationErrorFn);

            function startSimulationSuccessFn(){
                $.jGrowl("Simulation has been started successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function startSimulationErrorFn(){
                $.jGrowl("Simulation can't be started.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }

        }


    }

})();
