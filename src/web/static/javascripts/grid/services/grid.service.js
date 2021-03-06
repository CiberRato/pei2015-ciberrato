(function () {
    'use strict';

    angular
        .module("ciberonline.grid.services")
        .factory("Grid", Grid);

    Grid.$inject = ["$http"];

    function Grid($http) {
        var Grid = {
            create: create,
            getMyGrids: getMyGrids,
            getGrid: getGrid,
            destroy: destroy,
            getAgents: getAgents,
            associateAgent: associateAgent,
            disassociateAgent: disassociateAgent
        };

        return Grid;

        function create(teamName, competitionName){
            return $http.post('/api/v1/competitions/grid_position/', {
                competition_name: competitionName,
                team_name: teamName
            });
        }

        function getMyGrids(){
            return $http.get('/api/v1/competitions/grid_position/');
        }

        function getGrid(teamName, competitionName){
            return $http.get("/api/v1/competitions/grid_position/" + competitionName + "/?team_name=" + teamName);
        }
        function destroy(teamName, competitionName){
            return $http.delete('/api/v1/competitions/grid_position/' + competitionName + '/?team_name=' + teamName)
        }

        function getAgents(identifier){
            return $http.get("/api/v1/competitions/agent_grid/"+identifier+"/");
        }

        function associateAgent(agent_name, identifier, pos, teamName){
            return $http.post('/api/v1/competitions/agent_grid/', {
                grid_identifier: identifier,
                agent_name: agent_name,
                team_name: teamName,
                position: pos
            });
        }

        function disassociateAgent(identifier, pos){
            return $http.delete('/api/v1/competitions/agent_grid/' + identifier + '/?position=' + pos);
        }
    }

})();