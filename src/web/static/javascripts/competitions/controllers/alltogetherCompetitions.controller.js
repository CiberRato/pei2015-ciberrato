(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllTogetherCompetitionsController', AllTogetherCompetitionsController);

    AllTogetherCompetitionsController.$inject = ['$location', '$route', 'Competition'];

    function AllTogetherCompetitionsController($location, $route, Competition){
        var vm = this;
        vm.deleteCompetition = deleteCompetition;
        vm.changeState = changeState;

        activate();

        function activate(){
            Competition.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.competitions = data.data;
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
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
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/allCompetitions/');
            }

        }

        function changeState(name){
            var x = document.getElementById("select"+name).value;
            Competition.changeState(name, x).then(changeStateSuccessFn, changeStateErrorFn);

            function changeStateSuccessFn(){
                $.jGrowl("State of Competition has been changed successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function changeStateErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/panel/');
            }

        }

    }

})();

