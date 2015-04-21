(function () {
    'use strict';

    angular
        .module("ciberonline.rounds.services")
        .factory("Round", Round);

    Round.$inject = ["$http"];

    function Round($http) {
        var Round = {
            createRound: createRound,
            uploadParamList: uploadParamList,
            uploadGrid: uploadGrid,
            uploadLab: uploadLab,
            getSimulations: getSimulations,
            createSimulation: createSimulation,
            getGrids: getGrids,
            associateGrid: associateGrid,
            disassociateAgent: disassociateAgent,
            getSimulationGrids: getSimulationGrids,
            create: create,
            startSimulation: startSimulation,
            getRound: getRound,
            destroy: destroy,
            removeSimulation: removeSimulation,
            getSimulation: getSimulation,
            getFiles: getFiles,
            saveScore: saveScore,
            getScoresByTrial: getScoresByTrial,
            getScoresByRound: getScoresByRound
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
            return $http.get("/api/v1/competitions/trials_by_round/" + roundName + "/");
        }

        function createSimulation(roundName){
            return $http.post("/api/v1/competitions/trial/", {
                round_name: roundName
            });
        }
        function getGrids(competitionName){
            return $http.get("/api/v1/competitions/grid_positions_competition/" + competitionName + "/");
        }

        function getSimulationGrids(identifier){
            return $http.get("/api/v1/competitions/simulation_grid/" + identifier + "/");
        }

        function associateGrid(grid_identifier, simulation_identifier, pos){
            return $http.post("/api/v1/competitions/simulation_grid/", {
                grid_identifier: grid_identifier,
                simulation_identifier: simulation_identifier,
                position: pos
            });
        }

        function disassociateAgent(simulation_identifier, pos){
            return $http.delete("/api/v1/competitions/simulation_grid/" + simulation_identifier + "/?position=" + pos);
        }

        function create(roundName, competitionName){
            return $http.post("/api/v1/competitions/round/" , {
                name: roundName,
                parent_competition_name: competitionName
            })
        }

        function startSimulation(identifier){
            return $http.post("/api/v1/simulations/start/", {
                trial_id: identifier
            })
        }

        function getRound(roundName){
            return $http.get('/api/v1/competitions/round/' + roundName + '/');
        }

        function destroy(roundName){
            return $http.delete("/api/v1/competitions/round/" + roundName + "/");
        }

        function removeSimulation(identifier){
            return $http.delete("/api/v1/competitions/trial/" +identifier+"/");
        }

        function getSimulation(identifier){
            return $http.get("/api/v1/competitions/trial/" + identifier + "/");
        }

        function getFiles(roundName){
            return $http.get("/api/v1/competitions/round_files/" + roundName + "/");
        }

        function saveScore(identifier, team, score, agents, time){
            return $http.post("/api/v1/competitions/team_score/", {
                trial_id: identifier,
                team_name: team,
                score: score,
                number_of_agents: agents,
                time: time
            });
        }

        function getScoresByTrial(identifier){
            return $http.get("/api/v1/competitions/ranking_trial/" + identifier + "/");
        }

        function getScoresByRound(name){
            return $http.get("/api/v1/competitions/ranking_round/" + name +"/")
        }

    }
})();