(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('TrialsController', TrialsController);

    TrialsController.$inject = ['SoloTrials', '$routeParams', '$timeout', '$dragon'];

    function TrialsController(SoloTrials, $routeParams, $timeout, $dragon){
        var vm = this;
        vm.roundName = $routeParams.identifier;
        vm.launchTrial = launchTrial;
        vm.removeTrial = removeTrial;
        activate();

        function activate(){
            getTrials();

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
                    getTrials();
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

        function removeTrial(identifier){
            SoloTrials.removeTrial(identifier).then(removeTrialSuccessFn, removeTrialErrorFn);

            function removeTrialSuccessFn(){
                $.jGrowl("Trial has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    getTrials();
                });
            }

            function removeTrialErrorFn(data){
                console.error(data.data);
                $.jGrowl("Trial could not be removed.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });

            }

        }

        function getTrials(){
            SoloTrials.getTrials(vm.roundName).then(getTrialsSuccessFn, getTrialsErrorFn);

            function getTrialsSuccessFn(data){
                vm.trials = data.data;
                for(var i =0; i<vm.trials.trials.length; i++){
                    vm.trials.trials[i].total = vm.trials.trials[i].created_at.substr(0, vm.trials.trials[i].created_at.indexOf('.'));
                    vm.trials.trials[i].date = vm.trials.trials[i].total.substr(0, vm.trials.trials[i].created_at.indexOf('T'));
                    vm.trials.trials[i].hour = vm.trials.trials[i].total.substr(vm.trials.trials[i].created_at.indexOf('T')+1);

                    console.log(vm.trials.trials[i].hour);
                }
                $dragon.onReady(function() {
                    swampdragon.open(function () {
                        $dragon.onChannelMessage(function(channels, data) {
                            /*
                             if (data.data.message.status == 200){
                             $.jGrowl(data.data.message.content, {
                             life: 3500,
                             theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                             });
                             }else if(data.data.message.status == 400){
                             $.jGrowl(data.data.message.content, {
                             life: 3500,
                             theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                             });
                             }
                             */
                            if (data.data.message.trigger == 'trial_started' || data.data.message.trigger == 'trial_error' || data.data.message.trigger == 'trial_log'){
                                $timeout(function(){
                                    getTrials();
                                });
                            }

                            console.log(channels);
                            console.log(data.data._type);
                            console.log(data.data.message);
                        });
                    });
                });
                console.log(vm.trials);
            }


            function getTrialsErrorFn(data){
                console.error(data.data);
            }
        }

    }

})();