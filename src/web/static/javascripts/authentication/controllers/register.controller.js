(function(){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['$location', '$scope', 'Authentication'];

    function RegisterController($location, $scope, Authentication){
        var vm = this;

        vm.register = register;

        activate();

        function activate(){
            if(Authentication.isAuthenticated()){
                $location.url("/idp/register");
            }
        }

        function register() {
            Authentication.register(vm.email, vm.username, vm.first_name, vm.last_name, vm.password, vm.confirm_password, vm.teaching_institution);
        }
    }
})();