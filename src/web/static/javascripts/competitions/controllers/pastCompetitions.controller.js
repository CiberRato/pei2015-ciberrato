(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('PastCompetitionsController', PastCompetitionsController);

    PastCompetitionsController.$inject = ['$location', 'Competition', '$scope'];

    function PastCompetitionsController($location, Competition, $scope){
        var vm = this;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Competition.getPast().then(getPastSuccessFn, getPastErrorFn);

            function getPastSuccessFn(data){
                vm.competitions = data.data;
                for(var i = 0; i<vm.competitions.length; i++){
                    getTeams(vm.competitions[i].name, i);
                }
                $scope.loader = {
                    loading: true
                };
            }

            function getPastErrorFn(data){
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

    }

})();

