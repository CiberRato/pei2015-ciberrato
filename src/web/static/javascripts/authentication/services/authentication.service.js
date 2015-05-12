(function () {
    'use strict';

    angular
        .module("ciberonline.authentication.services")
        .factory("Authentication", Authentication);

    Authentication.$inject = ["$cookies", "$http", "$location"];

    function Authentication($cookies, $http, $location){
        var Authentication = {
            getAuthenticatedAccount: getAuthenticatedAccount,
            isAuthenticated: isAuthenticated,
            register: register,
            login: login,
            logout: logout,
            setAuthenticatedAccount: setAuthenticatedAccount,
            unauthenticate: unauthenticate,
            getCaptcha: getCaptcha
        };

        return Authentication;

        function login(email, password, hashkey, response){
            return $http.post("/api/v1/auth/login/", {
                email: email,
                password: password,
                hashkey: hashkey,
                response: response
            }).then(loginSuccessFn, loginErrorFn);
        }

        function loginSuccessFn(data){
            Authentication.setAuthenticatedAccount(data.data);
            window.location.assign('/panel/');
        }

        function loginErrorFn(data){
            console.error("Login Failure!");
            console.error(data.data);
            return data;
        }

        function register(email,username, first_name, last_name, password, confirm_password, teaching_institution){
            return $http.post("api/v1/accounts/",{
                email: email,
                password: password,
                confirm_password: confirm_password,
                username: username,
                first_name: first_name,
                last_name: last_name,
                teaching_institution: teaching_institution
            }).then(registerSuccessFn, registerErrorFn);
        }

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
            $.jGrowl(errors, {
                life: 5000,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
            });


        }

        function setAuthenticatedAccount(account){
            $cookies.authenticatedAccount = JSON.stringify(account);
        }

        function getAuthenticatedAccount() {
            if (!$cookies.authenticatedAccount) {
                return;
            }

            return JSON.parse($cookies.authenticatedAccount);
        }

        function isAuthenticated(){
            return !!$cookies.authenticatedAccount;
        }

        function unauthenticate() {
            delete $cookies.authenticatedAccount;
        }

        function logout(){
            return $http.post("api/v1/auth/logout/")
                .then(logoutSuccessFn, logoutErrorFn);
        }

        function logoutSuccessFn(){
            Authentication.unauthenticate();

            window.location.assign("/");
        }

        function logoutErrorFn(){
            console.error("Logout Failure!");
        }

        function getCaptcha(){
            return $http.get("api/v1/get_captcha/");
        }
    }
})();