(function(){

    'use strict';

    angular
        .module('cibexxnline.competitions.controllers')
        .controller('PastCompetitionsController', PastCompetitionsController);

    PastCompetitionsController.$inject = ['$location', 'Competition'];

    function PastCompetitionsController($location, Competition){
        var vm = this;
        activate();

        function activate(){
            Competition.getPast().then(getPastSuccessFn, getPastErrorFn);

            function getPastSuccessFn(data){
                vm.competitions = data.data;
                for(var i = 0; i<vm.competitions.length; i++){
                    getTeams(vm.competitions[i].name, i);
                }
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

                function getTeamsErrorFn(datag) {
                    console.error(data.data);
                    $location.path('/panel/')
                }
            }

        }

    }

})();

