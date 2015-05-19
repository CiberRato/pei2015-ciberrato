(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('AllChallengesController', AllChallengesController);

    AllChallengesController.$inject = ['$scope', 'Competition', '$timeout', 'Round'];

    function AllChallengesController($scope, Competition, $timeout, Round){
        var vm = this;
        vm.deleteChallenge = deleteChallenge;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            Competition.getAllRounds("Hall of fame - Single").then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

            function getHallOfFameSuccessFn(data){
                vm.challenges = data.data;
                console.log(vm.challenges);

                $scope.loader = {
                    loading: true
                };
            }

            function getHallOfFameErrorFn(data){
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

    }
})();