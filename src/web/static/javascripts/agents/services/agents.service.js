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
            $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";

            // estive a ver na net e ainda tens de ler a porra do ficheiro
            var r = new FileReader();
            var file = r.readAsBinaryString(value);
            console.log(file);

            // usa o debug do django para ver se consegues colocar primeiro ele a ler o 'file'
            return $http({
                url: '/api/v1/competitions/upload/agent/?agent_name=' + agentName + '&language=' +language,
                method: "POST",
                data: { file: 'test' }
            })
        }

        function destroy(agentName){
            return $http.delete("/api/v1/competitions/agent/"+ agentName +"/")
        }
    }
})();