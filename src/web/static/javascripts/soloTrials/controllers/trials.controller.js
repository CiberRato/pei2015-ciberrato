(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('TrialsController', TrialsController);

    TrialsController.$inject = ['SoloTrials', '$routeParams', '$timeout'];

    function TrialsController(SoloTrials, $routeParams, $timeout){
        var vm = this;
        vm.roundName = $routeParams.identifier;
        vm.launchTrial = launchTrial;
        activate();

        function activate(){
            SoloTrials.getTrials(vm.roundName).then(getTrialsSuccessFn, getTrialsErrorFn);

            function getTrialsSuccessFn(data){
                vm.trials = data.data;
                console.log(vm.trials);
            }


            function getTrialsErrorFn(data){
                console.error(data.data);
            }

        }

        function launchTrial(){

            SoloTrials.launchTrial(vm.roundName).then(launchSuccessFn, launchErrorFn);

            function launchSuccessFn(data){
                $.jGrowl("Trial has been created successfully", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                console.log(data.data);
                $timeout(function(){
                    SoloTrials.getTrials(vm.roundName).then(getTrialsSuccessFn, getTrialsErrorFn);

                    function getTrialsSuccessFn(data){
                        vm.trials = data.data;
                        console.log(vm.trials);
                    }


                    function getTrialsErrorFn(data){
                        console.error(data.data);
                    }
                });
            }

            function launchErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

    }

})();