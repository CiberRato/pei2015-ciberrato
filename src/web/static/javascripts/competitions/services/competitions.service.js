(function () {
    'use strict';

    angular
        .module("ciberonline.competitions.services")
        .factory("Competition", Competition);

    Competition.$inject = ["$http"];

    function Competition($http) {
        var Competition = {
            getAll: getAll,
            getAllAble: getAllAble,
            getCompetition: getCompetition,
            getTeams: getTeams,
            enroll: enroll,
            deleteEnroll: deleteEnroll,
            getMyCompetitions: getMyCompetitions,
            getPast: getPast,
            getLive: getLive,
            getMyTeams: getMyTeams,
            getCompetitions: getCompetitions,
            getFirstRound: getFirstRound,
            create: create,
            deleteCompetition: deleteCompetition,
            validateInscription: validateInscription,
            getAllRounds: getAllRounds,
            changeState: changeState,
            agents: agents,
            createTypeOfCompetition: createTypeOfCompetition,
            getAllTypesOfCompetition: getAllTypesOfCompetition,
            removeTypeOfCompetition: removeTypeOfCompetition,
            getType: getType,
            updateType: updateType,
            getValidByTeam: getValidByTeam,
            change: change,
            getScoresByCompetition: getScoresByCompetition

        };

        return Competition;

        function getAll(){
            return $http.get('/api/v1/competitions/get/All/');
        }
        function getAllAble(){
            return $http.get('/api/v1/competitions/get/Register/');
        }

        function getCompetition(competitionName){
            return $http.get('/api/v1/competitions/crud/' + competitionName +'/');
        }

        function getTeams(competitionName){
            return $http.get('/api/v1/competitions/groups/' + competitionName +'/');
        }

        function enroll(competitionName, teamName){
            return $http.post('/api/v1/competitions/enroll/',{
                competition_name: competitionName,
                group_name: teamName,
                valid: false
            });
        }

        function deleteEnroll(teamName, competitionName){
            return $http.delete('/api/v1/competitions/enroll/'+ competitionName + '/?group_name=' + teamName);
        }

        function getMyCompetitions(username){
            return $http.get('/api/v1/competitions/my_enrolled_groups/' + username + '/');
        }

        function getPast(){
            return $http.get('/api/v1/competitions/get/Past/');
        }

        function getLive(){
            return $http.get('/api/v1/competitions/get/Competition/');
        }

        function getMyTeams(username, competitionName){
            return $http.get("/api/v1/competitions/my_enrolled_groups_competition/" +username +"/?competition_name=" +competitionName);
        }

        function getCompetitions(competitionName){
            return $http.get("/api/v1/competitions/group_enrolled_competitions/" + competitionName+ "/");
        }

        function getFirstRound(competitionName){
            return $http.get("/api/v1/competitions/oldest_round/"+competitionName+"/");
        }

        function create(competitionName, type_of_competition){
            return $http.post("/api/v1/competitions/crud/", {
                name: competitionName,
                type_of_competition: type_of_competition
            });
        }

        function deleteCompetition(name){
            return $http.delete("/api/v1/competitions/crud/" +name+ "/");
        }

        function validateInscription(teamName, competitionName){
            return $http.post("/api/v1/competitions/toggle_group_inscription/", {
                competition_name: competitionName,
                group_name: teamName
            });
        }

        function getAllRounds(competitionName){
            return $http.get("/api/v1/competitions/rounds/" +competitionName +"/");
        }

        function changeState(name, state){
            return $http.put("/api/v1/competitions/state/" +name+ "/" , {
                state_of_competition: state
            });
        }

        function agents(groupName, competitionName){
            return $http.get("/api/v1/competitions/agents_by_competition_group/" + groupName+ "/?competition_name=" + competitionName)
        }

        function createTypeOfCompetition(typeName, teamsForTrial, agentsByGrid){
            return $http.post("/api/v1/competitions/type_of_competition/", {
                name: typeName,
                number_teams_for_trial: teamsForTrial,
                number_agents_by_grid: agentsByGrid
            });
        }

        function getAllTypesOfCompetition(){
            return $http.get("/api/v1/competitions/type_of_competition/");
        }

        function removeTypeOfCompetition(name){
            return $http.delete("/api/v1/competitions/type_of_competition/" + name + "/");
        }

        function getType(name){
            return $http.get("/api/v1/competitions/type_of_competition/" + name + "/");
        }

        function updateType(type, name){
            return $http.put("/api/v1/competitions/type_of_competition/" + name + "/", {
                name: type.name,
                number_teams_for_trial: type.number_teams_for_trial,
                number_agents_by_grid: type.number_agents_by_grid
            });
        }

        function getValidByTeam(teamName){
            return $http.get('/api/v1/competitions/enroll/' + teamName + '/');
        }

        function change(url){
            return $http.get(url);
        }

        function getScoresByCompetition(name){
            return $http.get("/api/v1/competitions/ranking_competition/" + name + "/");
        }



    }

})();