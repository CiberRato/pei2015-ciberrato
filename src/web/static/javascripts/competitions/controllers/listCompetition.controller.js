(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ListCompetitionController', ListCompetitionController);

    ListCompetitionController.$inject = ['$location', '$timeout', '$routeParams', 'Competition', 'Round'];

    function ListCompetitionController($location, $timeout, $routeParams, Competition, Round){
        var vm = this;
        vm.competitionName = $routeParams.name;
        vm.validateInscription = validateInscription;
        vm.getGrids = getGrids;
        vm.getScoresByTrial = getScoresByTrial;
        vm.getScoresByRound = getScoresByRound;
        vm.getScoresByCompetition = getScoresByCompetition;
        vm.identifier;

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
                    console.log(vm.rounds[i].simulations[k]);

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


        function validateInscription(group_name, competition_name, i){
            Competition.validateInscription(group_name, competition_name).then(validateInscriptionSuccessFn, validateInscriptionErrorFn);

            function validateInscriptionSuccessFn(){
                $timeout(function(){
                    Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                    function getTeamsSuccessFn(data) {
                        vm.competitionTeamsInfo = data.data;
                    }

                    function getTeamsErrorFn(data) {
                        console.error(data.data);
                        $location.url('/panel/');
                    }
                });            }
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

        function getScoresByTrial(){
            Round.getScoresByTrial(vm.identifier).then(getScoresByTrialSuccessFn, getScoresByTrialErrorFn);

            function getScoresByTrialSuccessFn(data){
                vm.scoresByTrial = data.data;
                console.log(vm.scoresByTrial);
            }

            function getScoresByTrialErrorFn(data){
                console.error(data.data);
            }


        }

        function getScoresByRound(name){
            Round.getScoresByRound(name).then(getScoresByRoundSuccessFn, getScoresByRoundErrorFn);

            function getScoresByRoundSuccessFn(data){
                vm.scoresByRound = data.data;
            }

            function getScoresByRoundErrorFn(data){
                console.error(data.data);
            }
        }

        function getScoresByCompetition(){
            Competition.getScoresByCompetition(vm.competitionName).then(getScoresByCompetitionSuccessFn, getScoresByCompetitionErrorFn);

            function getScoresByCompetitionSuccessFn(data){
                vm.scoresByCompetition = data.data;
            }

            function getScoresByCompetitionErrorFn(data){
                console.error(data.data);
            }
        }



    }

})();
