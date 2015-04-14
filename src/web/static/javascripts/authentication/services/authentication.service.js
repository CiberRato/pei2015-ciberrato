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
            $.jGrowl("Register Success.", {
                life: 2500,
                theme: 'btn-success'
            });
            $location.path('/idp/login/');
        }

        function registerErrorFn(data){
            var errors = "";
            console.error(data.data);
            try {
                if (data.data.message.email) {
                    if (data.data.message.email[0] == "This field is required."){
                        errors += "&bull; Email field is required<br/>";
                    }
                    if (data.data.message.email[0] == "This field must be unique.") {
                        errors += "&bull; Email already exists<br/>";
                    }
                    if (data.data.message.email[0] == "Enter a valid email address.") {
                        errors += "&bull; Invalid email<br/>";
                    }
                    if (data.data.message.email[0] == "This field may not be blank.") {
                        errors += "&bull; Email field is required<br/>";
                    }
                }

                if (data.data.message.first_name) {
                    if (data.data.message.first_name[0] == "This field is required.") {
                        errors += "&bull; First name field is required<br/>";
                    }
                    if (data.data.message.first_name[0] == "This field may not be blank.") {
                        errors += "&bull; First name field is required<br/>";
                    }
                    if (data.data.message.first_name[0] == "Ensure this field has at least 2 characters.") {
                        errors += "&bull; First name needs to have at least 2 characters<br/>";
                    }
                }

                if (data.data.message.last_name) {
                    if (data.data.message.last_name[0] == "This field is required.") {
                        errors += "&bull; Last name field is required<br/>";
                    }
                    if (data.data.message.last_name[0] == "This field may not be blank.") {
                        errors += "&bull; Last name field is required<br/>";
                    }
                    if (data.data.message.last_name[0] == "Ensure this field has at least 2 characters.") {
                        errors += "&bull; Last name needs to have at least 2 characters<br/>";
                    }
                }

                if (data.data.message.teaching_institution) {
                    if (data.data.message.teaching_institution[0] == "This field is required.") {
                        errors += "&bull; Teaching institution field is required<br/>";
                    }
                    if (data.data.message.teaching_institution[0] == "This field may not be blank.") {
                        errors += "&bull; Teaching institution field is required<br/>";
                    }
                    if (data.data.message.teaching_institution[0] == "Ensure this field has at least 2 characters.") {
                        errors += "&bull; Teaching institution needs to have at least 2 characters<br/>";
                    }

                }

                if (data.data.message.username) {
                    if(data.data.message.username[0] == "This field is required."){
                        errors += "&bull; Username field is required<br/>";
                    }
                    if (data.data.message.username[0] == "This field must be unique.") {
                        errors += "&bull; Username already taken<br/>";
                    }
                    if (data.data.message.username[0] == "This field may not be blank.") {
                        errors += "&bull; Username field is required<br/>";
                    }
                    if (data.data.message.username[0] == "Ensure this field has at least 2 characters.") {
                        errors += "&bull; Username needs to have at least 2 characters<br/>";
                    }

                }
            }catch (TypeError){

            }

            $.jGrowl(errors, {
                life: 5000,
                theme: 'btn-danger'
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
    }
})();