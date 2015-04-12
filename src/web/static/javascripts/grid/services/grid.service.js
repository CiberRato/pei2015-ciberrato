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
            destroy: destroy,
            getAgents: getAgents,
            associateAgent: associateAgent,
            disassociateAgent: disassociateAgent
        };

        return Grid;

        function create(teamName, competitionName){
            return $http.post('/api/v1/competitions/grid_position/', {
                competition_name: competitionName,
                group_name: teamName
            });
        }

        function getMyGrids(){
            return $http.get('/api/v1/competitions/grid_position/');
        }

        function destroy(teamName, competitionName){
            return $http.delete('/api/v1/competitions/grid_position/' + competitionName + '/?group_name=' + teamName)
        }

        function getAgents(identifier){
            return $http.get("/api/v1/competitions/agent_grid/"+identifier+"/");
        }

        function associateAgent(agent_name, identifier, pos){
            return $http.post('/api/v1/competitions/agent_grid/', {
                grid_identifier: identifier,
                agent_name: agent_name,
                position: pos
            });
        }

        function disassociateAgent(identifier, pos){
            return $http.delete('/api/v1/competitions/agent_grid/' + identifier + '/?position=' + pos);
        }
    }

})();