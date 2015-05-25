(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('ScoreChallengesController', ScoreChallengesController);

    ScoreChallengesController.$inject = ['$scope', '$routeParams', 'HallOfFame'];

    function ScoreChallengesController($scope, $routeParams, HallOfFame){
        var vm = this;
        vm.roundName = $routeParams.name;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            HallOfFame.getScores(vm.roundName).then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

            function getHallOfFameSuccessFn(data){
                vm.scores = data.data;
                console.log(vm.scores);

                $scope.loader = {
                    loading: true
                };
            }

            function getHallOfFameErrorFn(data){
                console.error(data.data);
            }

        }

    }
})();