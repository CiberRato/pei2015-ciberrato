(function(){

    'use strict';

    angular
        .module('ciberonline.statistics.controllers')
        .controller('StatisticsController', StatisticsController);

    StatisticsController.$inject = ['Statistics', '$scope', 'Notification'];

    function StatisticsController(Statistics, $scope, Notification){
        var vm = this;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Notification.activateNotifications();

            Statistics.getStats().then(getStatsSuccessFn, getStatsErrorFn);

            function getStatsSuccessFn(data){
                vm.stats = data.data;
                console.log(vm.stats);
                $scope.loader = {
                    loading: true
                };
            }

            function getStatsErrorFn(data){
                console.error(data.data);
            }

        }

    }

})();