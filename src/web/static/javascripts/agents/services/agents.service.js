(function () {
    'use strict';

    angular
        .module("ciberonline.agents.services")
        .factory("Agent", Agent);

    Agent.$inject = ["$cookies", "$http", "$location"];

    function Agent($cookies, $http, $location) {
        var Agent = {
            create: create,
            getByUser: getByUser
        };

        return Agent;

        function create(name, teamName, type){
            return $http.post('/api/v1/competitions/agent/',{
                agent_name: name,
                group_name: teamName,
                is_virtual: type
            })
        }

        function getByUser(username){
            return $http.get('/api/v1/competitions/agents_by_user/' + username + '/');
        }
    }
})();