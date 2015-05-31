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
        vm.getFiles = getFiles;
        vm.show = [];

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            Competition.getAllRounds("Hall of fame - Single").then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

            function getHallOfFameSuccessFn(data){
                vm.challenges = data.data;
                console.log(vm.challenges);

                Agent.getByUser(vm.username).then(getAgentsSuccessFn, getAgentsErrorFn);
                function getAgentsSuccessFn(data){
                    vm.agents = data.data;
                    for(var i=0; i<vm.agents.length; i++){
                        if(vm.agents[i].agent_name != "Remote"){
                            vm.show.push(vm.agents[i]);

                        }
                    }
                    console.log(vm.show);
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

        function getFiles(name){
            Round.getFile(name, "Hall of fame - Single", 'grid').then(getGridSuccessFn, getGridErrorFn);

            function getGridSuccessFn(data){
                vm.grid = data.data;
                Round.getFile(name, "Hall of fame - Single", 'lab').then(getLabSuccessFn, getLabErrorFn);

                function getLabSuccessFn(data){
                    vm.lab = data.data;

                }

                function getLabErrorFn(data){
                    console.error(data.data);
                }

            }

            function getGridErrorFn(data){
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
            var tmp = document.getElementById('select'+roundName);
            tmp = tmp.options[tmp.selectedIndex].value;
            console.log(tmp);
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



    }
})();