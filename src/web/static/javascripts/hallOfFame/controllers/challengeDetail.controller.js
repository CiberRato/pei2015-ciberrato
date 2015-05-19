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
                for(var i = 0; i<vm.trials.length; i++) {
                    vm.trials[i].total = vm.trials[i].created_at.substr(0, vm.trials[i].created_at.indexOf('.'));
                    vm.trials[i].date = vm.trials[i].total.substr(0, vm.trials[i].created_at.indexOf('T'));
                    vm.trials[i].hour = vm.trials[i].total.substr(vm.trials[i].created_at.indexOf('T') + 1);

                    getAgent(vm.trials[i].identifier, i);
                }


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

        function getAgent(identifier, i){
            Round.getAgentsByTrial(identifier).then(successFn, errorFn);

            function successFn(data){
                vm.trials[i].agent = data.data;
                console.log(data.data);
            }

            function errorFn(data){
                console.error(data.data);
            }
        }


        function launchTrial(){
            var tmp = document.getElementById('select').value;
            var agent = tmp.substr(0,tmp.indexOf(','));
            var team = tmp.substr(tmp.indexOf(',') + 1);
            console.log(team);
            HallOfFame.launchTrial(vm.roundName, agent, team).then(launchTrialSuccessFn, launchTrialErrorFn);

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