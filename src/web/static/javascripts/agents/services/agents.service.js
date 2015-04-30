(function () {
    'use strict';

    angular
        .module("ciberonline.agents.services")
        .factory("Agent", Agent);

    Agent.$inject = ["$http"];

    function Agent($http) {
        var Agent = {
            create: create,
            getByTeam: getByTeam,
            getValidByTeam: getValidByTeam,
            getByUser: getByUser,
            getAgent: getAgent,
            upload: upload,
            destroy: destroy,
            getFiles: getFiles,
            deleteUpload: deleteUpload,
            associate: associate,
            deleteAgent: deleteAgent,
            getLanguages: getLanguages,
            validateAgent: validateAgent,
            getFile: getFile
        };

        return Agent;

        function create(name, teamName, language){
            return $http.post('/api/v1/agents/agent/',{
                agent_name: name,
                team_name: teamName,
                language: language
            })
        }
        function getByTeam(teamName){
            return $http.get('/api/v1/agents/agents_by_team/' + teamName + '/');
        }

        function getValidByTeam(teamName){
            return $http.get('/api/v1/agents/agents_valid_by_team/' + teamName + '/');
        }

        function getByUser(username){
            return $http.get('/api/v1/agents/agents_by_user/' + username + '/');
        }

        function getAgent(name, teamName){
            return $http.get('/api/v1/agents/agent/' + name + '/?team_name=' + teamName);

        }

        function upload(agentName, value, teamName){
            var fd = new FormData();
            fd.append('file', value);

            return $http.post('/api/v1/agents/upload/agent/?agent_name=' + agentName + '&team_name=' + teamName, fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        }

        function validateAgent(agentName, teamName){
            return $http.post("/api/v1/agents/validate_code/", {
                agent_name: agentName,
                team_name: teamName
            });
        }

        function destroy(agentName, teamName){
            return $http.delete("/api/v1/agents/agent/"+ agentName + '/?team_name=' + teamName);
        }

        function getFiles(agentName, teamName){
            return $http.get("/api/v1/agents/agent_files/" + agentName + '/?team_name=' + teamName);
        }

        function deleteUpload(agentName, fileName, teamName){
            return $http.delete('/api/v1/agents/delete_agent_file/' + agentName + '/?file_name=' +fileName + '&team_name=' +teamName);
        }

        function associate(competitionName, agentName){
            return $http.post("/api/v1/competitions/associate_agent/", {
                competition_name: competitionName,
                agent_name: agentName
            });
        }

        function deleteAgent(agentName, teamName){
            return $http.delete("/api/v1/agents/agent/" + agentName + '/?team_name=' + teamName);
        }

        function getLanguages(){
            return $http.get('api/v1/agents/allowed_languages/');
        }

        function getFile(team_name, agent_name, file_name){
            return $http.get("/api/v1/agents/file/" + team_name + "/" + agent_name + "/" + file_name + "/");
        }

    }
})();