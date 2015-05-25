(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('TrialsController', TrialsController);

    TrialsController.$inject = ['SoloTrials', '$routeParams', '$timeout', '$dragon', '$scope', 'Notification'];

    function TrialsController(SoloTrials, $routeParams, $timeout, $dragon, $scope, Notification){
        var vm = this;
        vm.roundName = $routeParams.identifier;
        vm.launchTrial = launchTrial;
        vm.removeTrial = removeTrial;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

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
                        var round_notification = Notification.events.subscribe('notificationteam', 1, function(data){
                            console.log("TRIALS");

                            if (data.message.trigger == 'trial_started' || data.message.trigger == 'trial_error' || data.message.trigger == 'trial_log') {
                                round_trial();
                                console.log("entrei");
                            }

                            console.log(data._type);
                            console.log(data.message);
                        });
                        var round_trial = function(){
                            round_notification.remove();

                            $timeout(function () {
                                getTrials();
                            });
                        }
                    });
                });
                console.log(vm.trials);
                $scope.loader = {
                    loading: true
                };
            }

            function getTrialsErrorFn(data){
                console.error(data.data);
            }
        }

    }

})();