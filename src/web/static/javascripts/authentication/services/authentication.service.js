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
            loginWithCaptcha: loginWithCaptcha,
            logout: logout,
            setAuthenticatedAccount: setAuthenticatedAccount,
            unauthenticate: unauthenticate,
            getCaptcha: getCaptcha,
            resetPassword: resetPassword
        };

        return Authentication;

        function loginWithCaptcha(email, password, hashkey, response){
            return $http.post("/api/v1/auth/login/", {
                email: email,
                password: password,
                hashkey: hashkey,
                response: response
            });
        }
        function login(email, password){
            return $http.post("/api/v1/auth/login/", {
                email: email,
                password: password
            });
        }

        function register(email,username, first_name, last_name, password, confirm_password, teaching_institution, hashkey, response){
            return $http.post("api/v1/accounts/",{
                email: email,
                password: password,
                confirm_password: confirm_password,
                username: username,
                first_name: first_name,
                last_name: last_name,
                teaching_institution: teaching_institution,
                hashkey: hashkey,
                response: response

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

        function resetPassword(email){
            return $http.post("/api/v1/password_recover/request/", {
                email: email
            });
        }
    }
})();