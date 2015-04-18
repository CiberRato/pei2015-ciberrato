(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ListCompetitionController', ListCompetitionController);

    ListCompetitionController.$inject = ['$location', '$route', '$routeParams', 'Competition', 'Round'];

    function ListCompetitionController($location, $route, $routeParams, Competition, Round){
        var vm = this;
        vm.competitionName = $routeParams.name;
        vm.validateInscription = validateInscription;
        vm.getGrids = getGrids;

        activate();

        function activate() {
            Competition.getCompetition(vm.competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);
            Competition.getAllRounds(vm.competitionName).then(getAllRoundsSuccessFn, getAllRoundsErrorFn);

            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
                Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                function getTeamsSuccessFn(data) {
                    vm.competitionTeamsInfo = data.data;
                }

                function getTeamsErrorFn(data) {
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
                    console.log(vm.rounds[i].simulations);
                    for(var k = 0; k<vm.rounds[i].simulations.length; k++){
                        getGrids(vm.rounds[i].simulations[k].identifier, k, i);
                    }
                }

                function getSimulationsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');

                }
            }

            function getGrids(simulationIdentifier, k, i){
                Round.getSimulationGrids(simulationIdentifier, k, i).then(getSimulationGridsSuccessFn, getSimulationGridsErrorFn);

                function getSimulationGridsSuccessFn(data){
                    vm.rounds[i].simulations[k].grids = data.data;
                    console.log(vm.rounds[i].simulations[k].grids);

                }

                function getSimulationGridsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
            }

            function getAllRoundsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

<<<<<<< HEAD
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
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }
=======
>>>>>>> feature/Updates_angular

        function validateInscription(group_name, competition_name){
            Competition.validateInscription(group_name, competition_name).then(validateInscriptionSuccessFn, validateInscriptionErrorFn);

            function validateInscriptionSuccessFn(){
                $route.reload();            }
            function validateInscriptionErrorFn(data){
                console.error(data.data);
                $location.path('/admin/');
            }

        }

        function getGrids(identifier){
            Round.getSimulationGrids(identifier).then(getSimulationGridsSuccessFn, getSimulationGridsErrorFn);

            function getSimulationGridsSuccessFn(data){
                vm.grids = data.data;
                console.log(vm.grids);

            }

            function getSimulationGridsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

    }

})();
