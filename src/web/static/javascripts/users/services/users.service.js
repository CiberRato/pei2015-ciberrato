(function () {
    'use strict';

    angular
        .module("ciberonline.users.services")
        .factory("Users", Users);

    Users.$inject = ['$http'];

    function Users($http){
        var Users = {
            getAll: getAll,
            getMe: getMe,
            change: change,
            toggleStaff: toggleStaff,
            toggleSuperUser: toggleSuperUser
        };

        return Users;

        function getAll(){
            return $http.get('api/v1/accounts/');
        }

        function getMe(){
            return $http.get('api/v1/me/');
        }

        function change(url){
            return $http.get(url);
        }

        function toggleStaff(username){
            return $http.put("api/v1/toggle_staff/" + username + "/");
        }

        function toggleSuperUser(username){
            return $http.put("api/v1/toggle_super_user/" + username + "/");
        }
    }


})();