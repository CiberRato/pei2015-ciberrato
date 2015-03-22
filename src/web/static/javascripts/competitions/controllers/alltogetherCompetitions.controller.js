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

            function getAllSuccessFn(data, status, headers, config){
                vm.competitions = data.data;
            }

            function getAllErrorFn(data, status, headers, config){
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
                $.jGrowl("Competition can't be removed.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/allCompetitions/');
            }

        }

        function changeState(name){
            console.log(name);
            var x = document.getElementById("select").value;
            console.log(x);
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
                $.jGrowl("State of Competition can't be changed.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/panel/');
            }

        }

    }

})();

