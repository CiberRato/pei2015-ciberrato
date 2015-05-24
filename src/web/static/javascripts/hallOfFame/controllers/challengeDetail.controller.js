(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('ChallengeDetailController', ChallengeDetailController);

    ChallengeDetailController.$inject = ['$scope', 'Round', '$routeParams', 'Authentication', 'Notification'];

    function ChallengeDetailController($scope, Round, $routeParams, Authentication, Notification){
        var vm = this;
        vm.roundName = $routeParams.name;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();
        vm.username = authenticatedAccount.username;
        vm.show = [];

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            Notification.activateNotifications();


            Round.getTrials(vm.roundName, "Hall of fame - Single").then(getTrialsSuccessFn, getTrialsErrorFn);

            function getTrialsSuccessFn(data){
                vm.trials = data.data;
                console.log(vm.trials);

                for(var j = 0; j<vm.trials.length; j++){
                    if(vm.trials[j].state == "LOG"){
                       vm.show.push(vm.trials[j]);
                    }
                }
                for(var i = 0; i<vm.show.length; i++) {
                    vm.show[i].total = vm.show[i].created_at.substr(0, vm.show[i].created_at.indexOf('.'));
                    vm.show[i].date = vm.show[i].total.substr(0, vm.show[i].created_at.indexOf('T'));
                    vm.show[i].hour = vm.show[i].total.substr(vm.show[i].created_at.indexOf('T') + 1);

                    getAgent(vm.show[i].identifier, i);
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
                vm.show[i].agent = data.data;
                console.log(data.data);
            }

            function errorFn(data){
                console.error(data.data);
            }
        }




    }
})();