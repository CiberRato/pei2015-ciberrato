(function (){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('PanelController', PanelController);

    PanelController.$inject = ['$location', '$dragon', 'Notification', '$scope'];

    function PanelController($location, $dragon, Notification, $scope){
        var vm = this;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            Notification.activateNotifications();
            $scope.loader = {
                loading: true
            };
        }


    }
})();