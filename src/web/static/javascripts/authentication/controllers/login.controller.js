(function (){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', 'Authentication', '$scope'];

    function LoginController($location, Authentication, $scope){
        var vm = this;

        vm.login = login;
        vm.show_captcha = false;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            if(Authentication.isAuthenticated()){
                $location.url('/idp/login');
            }
            $scope.loader = {
                loading: true
            };
        }

        function getCaptchaSuccessFn(data){
            vm.captcha = data.data;
            console.log(vm.captcha);
            vm.count++;

        }

        function getCaptchaErrorFn(data){
            console.log(data.data);
        }

        function login(){
            if(vm.count >= 1){
                Authentication.loginWithCaptcha(vm.email, vm.password, vm.captcha.new_cptch_key, vm.captcha_text)
                    .then(loginSuccess, loginError);
            }else{
                Authentication.login(vm.email, vm.password)
                    .then(loginSuccess, loginError);
            }

        }

        function loginSuccess(data){
            Authentication.setAuthenticatedAccount(data.data);
            window.location.assign('/panel/');
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
            vm.show_captcha = true;

            Authentication.getCaptcha().then(getCaptchaSuccessFn, getCaptchaErrorFn);


        }
    }
})();