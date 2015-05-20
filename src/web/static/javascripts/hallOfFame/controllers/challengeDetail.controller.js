(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('ChallengeDetailController', ChallengeDetailController);

    ChallengeDetailController.$inject = ['$scope', 'Round', '$routeParams', 'Authentication'];

    function ChallengeDetailController($scope, Round, $routeParams, Authentication){
        var vm = this;
        vm.roundName = $routeParams.name;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();
        vm.username = authenticatedAccount.username;

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

                $scope.loader = {
                    loading: true
                };

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




    }
})();