(function () {
    'use strict';

    angular
        .module("ciberonline.rounds.services")
        .factory("Round", Round);

    Round.$inject = ["$cookies", "$http", "$location"];

    function Round($cookies, $http, $location) {
        var Round = {
            createRound: createRound,
            uploadParamList: uploadParamList,
            uploadGrid: uploadGrid,
            uploadLab: uploadLab,
            getSimulations: getSimulations,
            createSimulation: createSimulation,
            getAgents: getAgents,
            associateAgent: associateAgent,
            disassociateAgent: disassociateAgent,
            getSimulationAgents: getSimulationAgents,
            create: create,
            startSimulation: startSimulation,
            getRound: getRound,
            destroy: destroy,
            removeSimulation: removeSimulation
        };

        return Round;

        function createRound(roundName, competition){
            return $http.post("/api/v1/competitions/round/", {
                name: roundName,
                parent_competition_name: competition
            });
        }

        function uploadParamList(roundName, value){
            var fd = new FormData();
            fd.append('file', value);

            return $http.post('/api/v1/competitions/round/upload/param_list/?round=' + roundName, fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        }

        function uploadGrid(roundName, value){
            var fd = new FormData();
            fd.append('file', value);

            return $http.post('/api/v1/competitions/round/upload/grid/?round=' + roundName, fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        }

        function uploadLab(roundName, value){
            var fd = new FormData();
            fd.append('file', value);

            return $http.post('/api/v1/competitions/round/upload/lab/?round=' + roundName, fd, {
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
            });
        }

        function disassociateAgent(roundName, identifier, agent_name){
            console.log(roundName);
            console.log(agent_name);
            return $http.delete("/api/v1/competitions/associate_agent_to_simulation/" + identifier + "/?round_name=" +roundName+ "&agent_name=" +agent_name);
        }

        function create(roundName, competitionName){
            return $http.post("/api/v1/competitions/round/" , {
                name: roundName,
                parent_competition_name: competitionName
            })
        }

        function startSimulation(identifier){
            return $http.post("/api/v1/simulations/start/", {
                simulation_id: identifier
            })
        }

        function getRound(roundName){
            return $http.get('/api/v1/competitions/round/' + roundName + '/');
        }

        function destroy(roundName){
            return $http.delete("/api/v1/competitions/round/" + roundName + "/");
        }

        function removeSimulation(identifier){
            return $http.delete("/api/v1/competitions/simulation/" +identifier+"/");
        }

    }
})();