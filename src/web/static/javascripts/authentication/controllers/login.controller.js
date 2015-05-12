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
            Authentication.getCaptcha().then(getCaptchaSuccessFn, getCaptchaErrorFn);
        }

        function getCaptchaSuccessFn(data){
            vm.captcha = data.data;
            console.log(vm.captcha);
        }

        function getCaptchaErrorFn(data){
            console.log(data.data);
        }

        function login(){
            Authentication.login(vm.email, vm.password, vm.captcha.new_cptch_key, vm.captcha_text)
                .then(loginError);
        }

        function loginError(data){
            if(data){
                if(typeof data.data.detail !== 'undefined'){
                    $.jGrowl(data.data.detail, {
                        life: 2500,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                    });
                }else{
                    vm.error = data.data.error;
                    $.jGrowl("Username and/or password is wrong. ", {
                        life: 2500,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                    });
                }
            }
            Authentication.getCaptcha().then(getCaptchaSuccessFn, getCaptchaErrorFn);

        }
    }
})();