(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllTypesOfCompetitionController', AllTypesOfCompetitionController);

    AllTypesOfCompetitionController.$inject = ['$location', 'Competition', '$timeout', '$scope'];

    function AllTypesOfCompetitionController($location, Competition, $timeout, $scope){
        var vm = this;
        vm.deleteTypeOfCompetition = deleteTypeOfCompetition;
        vm.change = change;
        activate();


        function activate(){
            $scope.loader = {
                loading: false
            };

            Competition.getAllTypesOfCompetition().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.typesOfCompetitions = data.data;
                console.log(vm.typesOfCompetitions);
                $scope.loader = {
                    loading: true
                };
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

        }

        function deleteTypeOfCompetition(name){
            Competition.removeTypeOfCompetition(name).then(removeSuccessFn, removeErrorFn);

            function removeSuccessFn(){
                $.jGrowl("Type Of Competition has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });

                $timeout(function(){
                    Competition.getAllTypesOfCompetition().then(getAllSuccessFn, getAllErrorFn);

                    function getAllSuccessFn(data){
                        vm.typesOfCompetitions = data.data;
                    }

                    function getAllErrorFn(data){
                        console.error(data.data);
                        $location.url('/panel/');
                    }
                });
            }

            function removeErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function change(url){
            Competition.change(url).then(changeSuccessFn, changeErrorFn);

            function changeSuccessFn(data){
                vm.typesOfCompetitions = data.data;
            }

            function changeErrorFn(data){
                console.error(data.data);
            }
        }



    }

})();