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
            unauthenticate: unauthenticate
        };

        return Authentication;

        function login(email, password){
            return $http.post("/api/v1/auth/login/", {
                email: email,
                password: password
            }).then(loginSuccessFn, loginErrorFn);
        }

        function loginSuccessFn(data, status, headers, config){
            Authentication.setAuthenticatedAccount(data.data);
            window.location.assign('/profile/');
        }

        function loginErrorFn(data, status, headers, config){
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

        function registerSuccessFn(data, status, headers, config){
            $location.path('/idp/login/');
        }

        function registerErrorFn(data, status, headers, config){
            console.error("Registration Failure!");
            console.error(data.data);

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

        function logoutSuccessFn(data, status, headers, config){
            Authentication.unauthenticate();

            window.location.assign("/");
        }

        function logoutErrorFn(data, status, headers, config){
            console.error("Logout Failure!");
        }
    }
})();