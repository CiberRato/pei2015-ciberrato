(function () {
    'use strict';

    angular
        .module("ciberonline.users.services")
        .factory("Users", Users);

    Users.$inject = ['$http'];

    function Users($http){
        var Users = {
            getAll: getAll,
            change: change
        };

        return Users;

        function getAll(){
            return $http.get('api/v1/accounts/');
        }

        function change(url){
            return $http.get(url);
        }
    }


})();