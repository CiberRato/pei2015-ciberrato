(function () {
    'use strict';

    angular
        .module("ciberonline.competitions.services")
        .factory("Competition", Competition);

    Competition.$inject = ["$cookies", "$http", "$location"];

    function Competition($cookies, $http, $location) {
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
            getFirstRound: getFirstRound

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
            console.log(teamName + ' ' + competitionName);
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
            return $http.get("/api/v1/competitions/oldest_round/"+competitionName+"/")
        }
    }

})();