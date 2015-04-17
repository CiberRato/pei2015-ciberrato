(function () {
    'use strict';

    angular
        .module("ciberonline.profile.services")
        .factory("Profile", Profile);

    Profile.$inject = ['$http'];

    function Profile($http){
        var Profile = {
            getAll: getAll,
            get: get,
            update: update,
            updatePassword: updatePassword,
            destroy: destroy,
            getByFirstName: getByFirstName,
            getByLastName: getByLastName
        };

        return Profile;

        function getAll(){
            return $http.get('api/v1/accounts/');
        }

        function get(username) {
            return $http.get('/api/v1/accounts/' + username + '/');
        }

        function update(profile){
            return $http.put('/api/v1/accounts/' + profile.username + '/', profile);
        }

        function updatePassword(username, password, confirm_password){
            return $http.put('/api/v1/change_password/' + username + '/', {
                password: password,
                confirm_password: confirm_password
            });
        }

        function destroy(username){
            return $http.delete('/api/v1/accounts/' + username + '/');
        }

        function getByFirstName(name){
            return $http.get('/api/v1/account_by_first_name/' + name + '/');
        }

        function getByLastName(name){
            return $http.get('/api/v1/account_by_last_name/' + name + '/');
        }

    }


})();
