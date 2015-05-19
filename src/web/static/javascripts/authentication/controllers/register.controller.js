(function(){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['$location', 'Authentication', '$scope'];
    function RegisterController($location, Authentication, $scope){
        var vm = this;

        vm.register = register;
        vm.myFunction = myFunction;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            if(Authentication.isAuthenticated()){
                $location.url("/idp/register/");
            }

            Authentication.getCaptcha().then(getCaptchaSuccessFn, getCaptchaErrorFn);

        }

        function getCaptchaSuccessFn(data){
            vm.captcha = data.data;
            console.log(vm.captcha);
            $scope.loader = {
                loading: true
            };
        }

        function getCaptchaErrorFn(data){
            console.log(data.data);
        }

        function register() {
            console.log(vm.teaching_institution);
            Authentication.register(vm.email, vm.username, vm.first_name, vm.last_name, vm.password, vm.confirm_password, vm.teaching_institution, vm.captcha.new_cptch_key, vm.captcha_text).then(registerSuccessFn, registerErrorFn);

            function registerSuccessFn(){
                $.jGrowl("You have been successfully registered", {
                    life: 2500,
                    theme: 'btn-success'
                });
                $.jGrowl("Please check your inbox and confirm your email!", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all info'
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

        function myFunction(){
            var x = document.getElementById("select").value;
            console.log(x);
            if(x === "Other..."){
                $scope.input = true;
            }else{
                $scope.input = false;

            }
        }

    }
})();