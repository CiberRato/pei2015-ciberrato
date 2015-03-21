(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllCompetitionsController', AllCompetitionsController);

    AllCompetitionsController.$inject = ['$location', 'Competition'];

    function AllCompetitionsController($location, Competition){
        var vm = this;
        vm.deleteCompetition = deleteCompetition;
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
                    vm.competitions[i].allTeams = vm.teams.length;
                }

                function getTeamsErrorFn(data, status, headers, config) {
                    console.error(data.data);
                    $location.path('/panel/')
                }
            }

        }

        function deleteCompetition(name){
            Competition.deleteCompetition(name).then(deleteCompetitionSuccessFn, deleteCompetitionErrorFn);

            function deleteCompetitionSuccessFn(){
                $.jGrowl("Competition has been removed successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/allCompetitions/');
            }

            function deleteCompetitionErrorFn(){
                $.jGrowl("Competition can't be removed.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/allCompetitions/');
            }

        }

    }

})();
