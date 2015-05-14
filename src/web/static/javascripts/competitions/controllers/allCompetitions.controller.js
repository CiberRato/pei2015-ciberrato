(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllCompetitionsController', AllCompetitionsController);

    AllCompetitionsController.$inject = ['$location', 'Competition', '$scope'];

    function AllCompetitionsController($location, Competition, $scope){
        var vm = this;
        vm.getScoresByCompetition = getScoresByCompetition;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Competition.getAllAble().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.competitions = data.data;
                for(var i = 0; i<vm.competitions.length; i++){
                    getTeams(vm.competitions[i].name, i);
                }
                $scope.loader = {
                    loading: true
                };
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getTeams(competitionName, i) {
                Competition.getTeams(competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);


                function getTeamsSuccessFn(data) {
                    vm.teams = data.data;
                    vm.competitions[i].allTeams = vm.teams.length;
                }

                function getTeamsErrorFn(data) {
                    console.error(data.data);
                    $location.path('/panel/')
                }
            }

        }

        function getScoresByCompetition(name){
            Competition.getScoresByCompetition(name).then(getScoresByCompetitionSuccessFn, getScoresByCompetitionErrorFn);

            function getScoresByCompetitionSuccessFn(data){
                vm.scoresByCompetition = data.data;
            }

            function getScoresByCompetitionErrorFn(data){
                console.error(data.data);
            }
        }



    }

})();
