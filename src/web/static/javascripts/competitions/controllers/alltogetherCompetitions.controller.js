(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllTogetherCompetitionsController', AllTogetherCompetitionsController);

    AllTogetherCompetitionsController.$inject = ['$location', '$timeout', 'Competition', '$scope'];

    function AllTogetherCompetitionsController($location, $timeout, Competition, $scope){
        var vm = this;
        vm.deleteCompetition = deleteCompetition;
        vm.changeState = changeState;
        vm.getScoresByCompetition = getScoresByCompetition;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Competition.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.competitions = data.data;
                $scope.loader = {
                    loading: true
                };
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
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.path('/admin/allCompetitions/');
            }

            function deleteCompetitionErrorFn(){
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                $location.path('/admin/allCompetitions/');
            }

        }

        function changeState(name, state, i){
            var next;
            if(state === 'Register'){
                next = 'Competition';
            }else if(state === 'Competition'){
                next = 'Past'
            }else{
                next = 'Register';
            }
            Competition.changeState(name, next).then(changeStateSuccessFn, changeStateErrorFn);

            function changeStateSuccessFn(){
                $.jGrowl("State of Competition \""+ name +"\" has been changed to " + next + ".", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    Competition.getCompetition(name).then(getCompetitionSuccessFn, getCompetitionErrorFn);

                    function getCompetitionSuccessFn(data){
                        vm.competitions[i] = data.data;
                    }

                    function getCompetitionErrorFn(data){
                        console.error(data.data);
                    }
                });
            }

            function changeStateErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                $location.path('/panel/');
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

