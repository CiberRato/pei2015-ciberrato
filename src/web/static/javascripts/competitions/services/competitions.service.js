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
            getMyCompetitions: getMyCompetitions

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
    }

})();