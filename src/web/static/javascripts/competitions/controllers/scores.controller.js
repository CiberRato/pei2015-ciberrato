(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ScoresController', ScoresController);

    ScoresController.$inject = ['$location', '$routeParams', 'Competition', 'Round', '$scope', 'Notification'];

    function ScoresController($location, $routeParams, Competition, Round, $scope, Notification){
        var vm = this;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Notification.activateNotifications();

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
                    $scope.loader = {
                        loading: true
                    };
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
                if(i == vm.rounds.length-1){
                    vm.rounds[i].first_round = false;
                    vm.rounds[i].last_round = true;
                }else if(i == 0){
                    vm.rounds[i].first_round = true;
                    vm.rounds[i].last_round = false;
                }else{
                    vm.rounds[i].first_round = false;
                    vm.rounds[i].last_round = false;
                }
                if(vm.rounds[i].first_round === false && vm.rounds[i].last_round === false){
                    for(var k = 0; k<vm.rounds[i].scores.length; k++){
                        for(var j = 0; j<vm.rounds[i-1].scores.length; j++){
                            if(vm.rounds[i].scores[k].team.name === vm.rounds[i-1].scores[j].team.name) {
                                vm.rounds[i].scores[k].score += vm.rounds[i-1].scores[j].score;
                                vm.rounds[i].scores[k].number_of_agents += vm.rounds[i-1].scores[j].number_of_agents;
                                vm.rounds[i].scores[k].time += vm.rounds[i-1].scores[j].time;
                            }
                        }

                    }

                }            }

            function getScoresErrorFn(data){
                console.error(data.data);
            }
        }


    }
})();
