(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ScoresController', ScoresController);

    ScoresController.$inject = ['$location', '$routeParams', 'Competition', 'Round'];

    function ScoresController($location, $routeParams, Competition, Round){
        var vm = this;

        activate();

        function activate(){
            vm.competitionName = $routeParams.name;
            Competition.getCompetition(vm.competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);
            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
                Competition.getAllRounds(vm.competitionName).then(getAllRoundsSuccessFn, getAllRoundsErrorFn);
                function getAllRoundsSuccessFn(data){
                    vm.rounds = data.data;
                    for(var i = 0; i<vm.rounds.length; i++){
                        getScore(vm.rounds[i].name, i);
                    }
                    Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                    function getTeamsSuccessFn(data){
                        vm.teams = data.data;
                    }


                    function getTeamsErrorFn(data){
                        console.error(data.data);
                    }
                }

                function getAllRoundsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
            }

            function getCompetitionErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

        }

        function getScore(name, i){
            Round.getScoresByRound(name, vm.competitionName).then(getScoresSuccessFn, getScoresErrorFn);

            function getScoresSuccessFn(data){
                vm.rounds[i].scores = data.data;
            }

            function getScoresErrorFn(data){
                console.error(data.data);
            }



        }

    }
})();
