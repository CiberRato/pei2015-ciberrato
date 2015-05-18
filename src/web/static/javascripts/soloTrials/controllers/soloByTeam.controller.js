(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('SoloByTeamController', SoloByTeamController);

    SoloByTeamController.$inject = ['SoloTrials', '$routeParams', '$timeout', '$scope'];

    function SoloByTeamController(SoloTrials, $routeParams, $timeout, $scope){
        var vm = this;
        vm.competitionName = $routeParams.identifier;
        vm.teamName = $routeParams.teamName;
        vm.deleteSoloTrial = deleteSoloTrial;
        vm.getGrid = getGrid;
        vm.getLab = getLab;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            SoloTrials.getByTeam(vm.competitionName).then(getByTeamSuccessFn, getByTeamErrorFn);

            function getByTeamSuccessFn(data){
                vm.solos = data.data;
                console.log(vm.solos);
                $scope.loader = {
                    loading: true
                };
            }


            function getByTeamErrorFn(data){
                console.error(data.data);
            }


        }

        function deleteSoloTrial(name){
            SoloTrials.removeSoloTrial(name).then(removeSoloTrialSuccessFn, removeSoloTrialErrorFn);

            function removeSoloTrialSuccessFn(){
                $.jGrowl("Solo Trial has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    SoloTrials.getByTeam(vm.competitionName).then(getByTeamSuccessFn, getByTeamErrorFn);

                    function getByTeamSuccessFn(data){
                        vm.solos = data.data;
                        console.log(vm.solos);
                    }


                    function getByTeamErrorFn(data){
                        console.error(data.data);
                    }                });
            }

            function removeSoloTrialErrorFn(data){
                console.error(data.data);
                $.jGrowl("Solo Trial could not be removed.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function getGrid(grid){

            SoloTrials.getResource(grid).then(getResourceSuccessFn, getResourceErrorFn);

            function getResourceSuccessFn(data){
                vm.grid = data.data;
                console.log(data.data);
            }
        }

        function getLab(lab){
            console.log(lab);
            SoloTrials.getResource(lab).then(getResourceSuccessFn, getResourceErrorFn);

            function getResourceSuccessFn(data){
                vm.lab = data.data;
                console.log(data.data);
            }
        }

        function getResourceErrorFn(data){
            console.error(data.data);
        }

    }

})();