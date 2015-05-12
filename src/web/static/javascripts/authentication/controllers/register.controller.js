(function(){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['$location', 'Authentication'];

    function RegisterController($location, Authentication){
        var vm = this;

        vm.register = register;

        activate();

        function activate(){
            if(Authentication.isAuthenticated()){
                $location.url("/idp/register/");
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

        function register() {
            Authentication.register(vm.email, vm.username, vm.first_name, vm.last_name, vm.password, vm.confirm_password, vm.teaching_institution, vm.captcha.new_cptch_key, vm.captcha_text).then(registerSuccessFn, registerErrorFn);

            function registerSuccessFn(){
                $.jGrowl("You have been successfully registered", {
                    life: 2500,
                    theme: 'btn-success'
                });
                $location.path('/idp/login/');
            }

            function registerErrorFn(data){
                var errors = "";
                for (var value in data.data.message) {
                    errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                    for (var error in data.data.message[value]){
                        errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                    }
                }
                if(typeof data.data.detail !== 'undefined'){
                    errors += " &nbsp; "+ data.data.detail + '<br/>';
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                Authentication.getCaptcha().then(getCaptchaSuccessFn, getCaptchaErrorFn);



            }
        }

    }
})();