(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('ChallengeDetailController', ChallengeDetailController);

    ChallengeDetailController.$inject = ['$scope', '$timeout', 'Round', '$routeParams', 'Authentication', 'Agent', 'HallOfFame'];

    function ChallengeDetailController($scope, $timeout, Round, $routeParams, Authentication, Agent, HallOfFame){
        var vm = this;
        vm.roundName = $routeParams.name;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();
        vm.username = authenticatedAccount.username;
        vm.launchTrial = launchTrial;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            Round.getTrials(vm.roundName, "Hall of fame - Single").then(getTrialsSuccessFn, getTrialsErrorFn);

            function getTrialsSuccessFn(data){
                vm.trials = data.data;
                console.log(vm.trials);

                Agent.getByUser(vm.username).then(getAgentsSuccessFn, getAgentsErrorFn);

                function getAgentsSuccessFn(data){
                    vm.agents = data.data;
                    $scope.loader = {
                        loading: true
                    };
                }

                function getAgentsErrorFn(data){
                    console.error(data.data);
                }


            }

            function getTrialsErrorFn(data) {
                console.error(data.data);
            }

        }


        function launchTrial(){
            var agent = document.getElementById('select').value;
            console.log(agent);
            HallOfFame.launchTrial(vm.roundName, agent).then(launchTrialSuccessFn, launchTrialErrorFn);

            function launchTrialSuccessFn(data){
                $.jGrowl("Trial has been created successfully", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                console.log(data.data);
                $timeout(function(){
                    Round.getTrials(vm.roundName, "Hall of fame - Single").then(getTrialsSuccessFn, getTrialsErrorFn);

                    function getTrialsSuccessFn(data){
                        vm.trials = data.data;
                        console.log(vm.trials);

                        Agent.getByUser(vm.username).then(getAgentsSuccessFn, getAgentsErrorFn);

                        function getAgentsSuccessFn(data){
                            vm.agents = data.data;
                            $scope.loader = {
                                loading: true
                            };
                        }

                        function getAgentsErrorFn(data){
                            console.error(data.data);
                        }


                    }

                    function getTrialsErrorFn(data) {
                        console.error(data.data);
                    }
                });
            }

            function launchTrialErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

    }
})();