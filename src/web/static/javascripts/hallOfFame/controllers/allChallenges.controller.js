(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('AllChallengesController', AllChallengesController);

    AllChallengesController.$inject = ['$scope', 'Competition', '$timeout', 'Round', 'Authentication', 'Agent', 'HallOfFame'];

    function AllChallengesController($scope, Competition, $timeout, Round, Authentication, Agent, HallOfFame){
        var vm = this;
        vm.deleteChallenge = deleteChallenge;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();
        vm.username = authenticatedAccount.username;
        vm.launchTrial = launchTrial;
        vm.getGrid = getGrid;
        vm.getLab = getLab;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            Competition.getAllRounds("Hall of fame - Single").then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

            function getHallOfFameSuccessFn(data){
                vm.challenges = data.data;
                for(var i = 0; i<vm.challenges.length; i++){
                    getFiles(vm.challenges[i].name, i);
                }

                console.log(vm.challenges);

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

            function getHallOfFameErrorFn(data){
                console.error(data.data);
            }



        }

        function getFiles(name, i){
            Round.getFiles(name, "Hall of fame - Single").then(getFilesSuccessFn, getFilesErrorFn);

            function getFilesSuccessFn(data){
                vm.challenges[i].files = data.data;
            }

            function getFilesErrorFn(data){
                console.error(data.data);
            }
        }


        function deleteChallenge(name){
            Round.destroy(name, "Hall of fame - Single").then(deleteChallengeSuccessFn, deleteChallengeErrorFn);

            function deleteChallengeSuccessFn(){
                $.jGrowl("Challenge has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function() {
                    Competition.getAllRounds("Hall of fame - Single").then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

                    function getHallOfFameSuccessFn(data) {
                        vm.challenges = data.data;
                        console.log(vm.challenges);
                        $scope.loader = {
                            loading: true
                        };
                    }

                    function getHallOfFameErrorFn(data) {
                        console.error(data.data);
                    }
                });
            }

            function deleteChallengeErrorFn(data){
                console.error(data.data);
                $.jGrowl("Challenge could not be removed.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function launchTrial(roundName){
            var tmp = document.getElementById('select').value;
            var agent = tmp.substr(0,tmp.indexOf(','));
            var team = tmp.substr(tmp.indexOf(',') + 1);

            HallOfFame.launchTrial(roundName, agent, team).then(launchTrialSuccessFn, launchTrialErrorFn);

            function launchTrialSuccessFn(data){
                $.jGrowl("Trial has been created successfully", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                console.log(data.data);
                $timeout(function(){
                    Round.getTrials(roundName, "Hall of fame - Single").then(getTrialsSuccessFn, getTrialsErrorFn);

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

        function getGrid(grid){

            SoloTrials.getResource(grid).then(getResourceSuccessFn, getResourceErrorFn);

            function getResourceSuccessFn(data) {
                vm.grid = data.data;
            }
        }

        function getLab(lab){

            SoloTrials.getResource(lab).then(getResourceSuccessFn, getResourceErrorFn);

            function getResourceSuccessFn(data){
                vm.lab = data.data;
            }

        }

        function getResourceErrorFn(data){
            console.error(data.data);
        }

    }
})();