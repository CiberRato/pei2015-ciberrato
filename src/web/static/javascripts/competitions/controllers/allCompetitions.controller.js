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
            Competition.getAll().then(getAllSuccessFn, getAllErrorFn);

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
                Competition.getNotValidTeams(competitionName).then(getNotValidTeamsSuccessFn, getNotValidTeamsErrorFn);


                function getNotValidTeamsSuccessFn(data, status, headers, config) {
                    vm.notValidTeams = data.data;
                    vm.competitions[i].allTeams = vm.notValidTeams.length;
                }

                function getNotValidTeamsErrorFn(data, status, headers, config) {
                    console.error(data.data);
                    $location.path('/panel/')
                }
            }

        }


    }

})();
