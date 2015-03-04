(function(){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('LogoutController', LogoutController);

    LogoutController.$inject = ['$scope', 'Authentication'];

    function LogoutController($scope, Authentication){
        var vm = this;

        $scope.vm = vm;

        vm.logout = logout;

        function logout(){
            Authentication.logout();
        }
    }
})();
