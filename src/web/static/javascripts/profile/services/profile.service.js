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
            change: change,
            getBroadcastNotifications: getBroadcastNotifications,
            getAdminNotifications: getAdminNotifications,
            getUserNotifications: getUserNotifications,
            getTeamNotifications: getTeamNotifications
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

        function change(url){
            return $http.get(url);
        }

        function getBroadcastNotifications(){
            return $http.get("/api/v1/notifications/broadcast/");
        }

        function getAdminNotifications(){
            return $http.get("/api/v1/notifications/admin/");
        }

        function getUserNotifications(){
            return $http.get("/api/v1/notifications/user/");
        }

        function getTeamNotifications(){
            return $http.get("/api/v1/notifications/teams/");
        }

    }


})();
