(function () {
    'use strict';

    angular
        .module("ciberonline.teams.services")
        .factory("Team", Team);

    Team.$inject = ['$http'];

    function Team($http){
        var Team = {
            create: create
        };

        return Team;

        function create(name, max_members){
            return $http.post('api/v1/groups/crud/', {
                name: name,
                max_members: max_members
            }).then(createSuccessFn, createErrorFn);

        }

        function createSuccessFn(data, status, headers, config){
            $location.path('/idp/panel/:username/myTeams/');
        }

        function createErrorFn(data, status, headers, config){
            console.error(data.data);
        }

    }


})();

