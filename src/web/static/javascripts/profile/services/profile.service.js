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
            destroy: destroy
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

        function destroy(username){
            return $http.delete('/api/v1/accounts/' + username + '/');
        }

    }


})();
