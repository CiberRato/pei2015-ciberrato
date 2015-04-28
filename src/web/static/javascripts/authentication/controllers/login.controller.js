(function (){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', '$dragon', 'Authentication'];

    function LoginController($location, $dragon, Authentication){
        var vm = this;

        vm.login = login;

        activate();

        function activate(){
            if(Authentication.isAuthenticated()){
                $location.url('/idp/login');
            }
        }

        function login(){
            Authentication.login(vm.email, vm.password)
                .then(loginError);
        }

        function loginError(data){
            if(data){
                vm.error = data.data.error;
                $.jGrowl("Username and/or password is wrong. ", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }
    }
})();