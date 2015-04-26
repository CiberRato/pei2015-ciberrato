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
            console.log("AQUI");
            /* SUBSCRIBE */
            /// Subscribe to the chat router
            $dragon.onReady(function() {
                $dragon.subscribe('notifications', 'notifications', null, function (context, data) {
                    // any thing that happens after successfully subscribing
                    console.log("// any thing that happens after successfully subscribing");
                }, function (context, data) {
                    // any thing that happens if subscribing failed
                    console.log("// any thing that happens if subscribing failed");
                });
            });

            $dragon.onChannelMessage(function(channels, data) {
                console.log(data.data.message);
            });
            Authentication.login(vm.email, vm.password)
                .then(loginError);
        }

        function loginError(data){
            if(data){
                vm.error = data.data.error;
                $.jGrowl("Username and/or password is wrong. ", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }
    }
})();