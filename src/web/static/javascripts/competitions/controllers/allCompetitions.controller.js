(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllCompetitionsController', AllCompetitionsController);

    AllCompetitionsController.$inject = ['$location', 'Competition'];

    function AllCompetitionsController($location, Competition){
        var vm = this;
        activate();

        function activate(){
            Competition.getAllAble().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data, status, headers, config){
                vm.competitions = data.data;
                for(var i = 0; i<vm.competitions.length; i++){
                    getTeams(vm.competitions[i].name, i);
                }
            }

            function getAllErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getTeams(competitionName, i) {
                Competition.getTeams(competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);


                function getTeamsSuccessFn(data, status, headers, config) {
                    vm.teams = data.data;
                    console.log(vm.teams.length);
                    vm.competitions[i].allTeams = vm.teams.length;
                }

                function getTeamsErrorFn(data, status, headers, config) {
                    console.error(data.data);
                    $location.path('/panel/')
                }
            }

        }

    }

})();
