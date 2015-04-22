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
                    getTrials(vm.rounds[i].name, i);
                }
            }

            function getTrials(roundName, i){
                Round.getTrials(roundName).then(getTrialsSuccessFn, getTrialsErrorFn);

                function getTrialsSuccessFn(data){
                    vm.rounds[i].trials = data.data;
                    console.log(vm.rounds[i].trials);
                    for(var k = 0; k<vm.rounds[i].trials.length; k++){
                        getGrids(vm.rounds[i].trials[k].identifier, k, i);
                    }
                }

                function getTrialsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');

                }
            }

            function getGrids(trialIdentifier, k, i){
                Round.getTrialGrids(trialIdentifier, k, i).then(getTrialGridsSuccessFn, getTrialGridsErrorFn);

                function getTrialGridsSuccessFn(data){
                    vm.rounds[i].trials[k].grids = data.data;
                    console.log(vm.rounds[i].trials[k]);

                }

                function getTrialGridsErrorFn(data){
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
            Round.getTrialGrids(identifier).then(getTrialGridsSuccessFn, getTrialGridsErrorFn);

            function getTrialGridsSuccessFn(data){
                vm.grids = data.data;
                console.log(vm.grids);

            }

            function getTrialGridsErrorFn(data){
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
