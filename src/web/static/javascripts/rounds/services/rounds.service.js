(function () {
    'use strict';

    angular
        .module("ciberonline.rounds.services")
        .factory("Round", Round);

    Round.$inject = ["$cookies", "$http", "$location"];

    function Round($cookies, $http, $location) {
        var Round = {
            createRound: createRound,
            upload: upload,
            getSimulations: getSimulations,
            createSimulation: createSimulation,
            getAgents: getAgents,
            associateAgent: associateAgent,
            getSimulationAgents: getSimulationAgents
        };

        return Round;

        function createRound(roundName, competition){
            return $http.post("/api/v1/competitions/round/", {
                name: roundName,
                parent_competition_name: competition
            });
        }

        function upload(agentName, language, value){
            var fd = new FormData();
            fd.append('file', value);

            return $http.post('/api/v1/competitions/upload/agent/?agent_name=' + agentName + '&language=' +language, fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        }

        function getSimulations(roundName){
            return $http.get("/api/v1/competitions/simulations_by_round/" + roundName + "/");
        }

        function createSimulation(roundName){
            return $http.post("/api/v1/competitions/simulation/", {
                round_name: roundName
            });
        }
        function getAgents(roundName){
            return $http.get("/api/v1/competitions/valid_round_agents/" +roundName+"/");
        }

        function getSimulationAgents(identifier){
            return $http.get("/api/v1/competitions/simulation_agents/" + identifier + "/");
        }

        function associateAgent(roundName, identifier, agent_name, pos){
            return $http.post("/api/v1/competitions/associate_agent_to_simulation/", {
                round_name: roundName,
                simulation_identifier: identifier,
                agent_name: agent_name,
                pos: pos
            })
        }

    }
})();