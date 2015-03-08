(function () {
    'use strict';

    angular
        .module("ciberonline.teams.services")
        .factory("Team", Team);

    Team.$inject = ['$http'];

    function Team($http){
        var Team = {
            create: create,
            getAll: getAll,
            getByUser: getByUser
        };

        return Team;

        function create(name, max_members){
            return $http.post('api/v1/groups/crud/', {
                name: name,
                max_members: max_members
            });

        }

        function getAll(){
            return $http.get('api/v1/groups/crud/');
        }

        function getByUser(username){
            console.log(username);
            return $http.get('api/v1/groups/user/' + username + '/');
        }

    }


})();

