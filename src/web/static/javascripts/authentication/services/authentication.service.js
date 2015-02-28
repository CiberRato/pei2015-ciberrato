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
            login: login,
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

            window.location = "/";
        }

        function loginErrorFn(data, status, headers, config){
            console.error("Login Failure!");
            console.error(data.data);
            return data;
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
    }
})();