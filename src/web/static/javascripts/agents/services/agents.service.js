(function () {
    'use strict';

    angular
        .module("ciberonline.agents.services")
        .factory("Agent", Agent);

    Agent.$inject = ["$http"];

    function Agent($http) {
        var Agent = {
            create: create,
            getByGroup: getByGroup,
            getByUser: getByUser,
            getAgent: getAgent,
            upload: upload,
            destroy: destroy,
            getFiles: getFiles,
            deleteUpload: deleteUpload,
            associate: associate,
            deleteAgent: deleteAgent,
            getLanguages: getLanguages,
        };

        return Agent;

        function create(name, teamName, type){
            return $http.post('/api/v1/agents/agent/',{
                agent_name: name,
                group_name: teamName,
                is_virtual: type
            })
        }
        function getByGroup(teamName){
            return $http.get('/api/v1/agents/agents_by_group/' + teamName + '/');
        }

        function getByUser(username){
            return $http.get('/api/v1/agents/agents_by_user/' + username + '/');
        }

        function getAgent(name){
            return $http.get('/api/v1/agents/agent/' + name + '/');

        }

        function upload(agentName, language, value){
            var fd = new FormData();
            fd.append('file', value);

            return $http.post('/api/v1/agents/upload/agent/?agent_name=' + agentName + '&language=' +language, fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        }

        function destroy(agentName){
            return $http.delete("/api/v1/agents/agent/"+ agentName +"/");
        }

        function getFiles(agentName){
            return $http.get("/api/v1/agents/agent_files/" + agentName + "/");
        }

        function deleteUpload(agentName, fileName){
            return $http.delete('/api/v1/agents/delete_agent_file/' + agentName + '/?file_name=' +fileName);
        }

        function associate(competitionName, agentName){
            return $http.post("/api/v1/competitions/associate_agent/", {
                competition_name: competitionName,
                agent_name: agentName
            });
        }

        function deleteAgent(agentName){
            return $http.delete("/api/v1/agents/agent/" + agentName + "/");
        }

        function getLanguages(){
            return $http.get('api/v1/agents/allowed_languages/');
        }

    }
})();