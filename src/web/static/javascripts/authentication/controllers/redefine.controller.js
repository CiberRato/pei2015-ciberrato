(function (){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('RedefineController', RedefineController);

    RedefineController.$inject = ['$location', 'Notification', 'Authentication', '$scope', '$routeParams'];

    function RedefineController($location, Notification, Authentication, $scope, $routeParams){
        var vm = this;

        vm.redefinePassword = redefinePassword;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            vm.token = $routeParams.token;
            Notification.activateNotifications();
            if(Authentication.isAuthenticated()){
                $location.url('/idp/login');
            }
            $scope.loader = {
                loading: true
            };
        }

        function redefinePassword() {
            Authentication.redefinePassword(vm.token, vm.password, vm.confirm_password).then(redefinePasswordSuccessFn, redefinePasswordErrorFn);

            function redefinePasswordSuccessFn() {
                $.jGrowl("Your Password has been updated successfully!", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all info'
                });
                $location.path('/idp/login/');
            }

            function redefinePasswordErrorFn(data) {
                console.error(data.data);
            }
        }

    }
})();