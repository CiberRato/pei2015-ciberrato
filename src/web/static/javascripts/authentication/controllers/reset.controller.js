(function (){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('ResetController', ResetController);

    ResetController.$inject = ['$location', 'Notification', 'Authentication', '$scope'];

    function ResetController($location, Notification, Authentication, $scope){
        var vm = this;

        vm.resetPassword = resetPassword;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Notification.activateNotifications();
            if(Authentication.isAuthenticated()){
                $location.url('/idp/login');
            }
            $scope.loader = {
                loading: true
            };
        }

        function resetPassword(){
            Authentication.resetPassword(vm.email).then(resetPasswordSuccessFn, resetPasswordErrorFn);

            function resetPasswordSuccessFn(){
                $.jGrowl("Please check your inbox!", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all info'
                });
                $location.path('/idp/login/');
            }

            function resetPasswordErrorFn(data){
                console.error(data.data);
            }
        }

    }
})();