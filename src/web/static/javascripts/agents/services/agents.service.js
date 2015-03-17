(function () {
    'use strict';

    angular
        .module("ciberonline.agents.services")
        .factory("Agent", Agent);

    Agent.$inject = ["$cookies", "$http", "$location"];

    function Agent($cookies, $http, $location) {
        var Agent = {
            create: create,
            getByGroup: getByGroup,
            getByUser: getByUser,
            getAgent: getAgent,
            upload: upload,
            destroy: destroy
        };

        return Agent;

        function create(name, teamName, type){
            return $http.post('/api/v1/competitions/agent/',{
                agent_name: name,
                group_name: teamName,
                is_virtual: type
            })
        }
        function getByGroup(teamName){
            return $http.get('/api/v1/competitions/agents_by_group/' + teamName + '/');
        }

        function getByUser(username){
            return $http.get('/api/v1/competitions/agents_by_user/' + username + '/');
        }

        function getAgent(name){
            return $http.get('/api/v1/competitions/agent/' + name + '/');

        }

        function upload(agentName, language, value){
            console.log(value);
            return $http.post('/api/v1/competitions/upload/agent/?agent_name=' + agentName + '&language=' +language,{
                file: value
            });
        }

        function destroy(agentName){
            return $http.delete("/api/v1/competitions/agent/"+ agentName +"/")
        }
    }
})();