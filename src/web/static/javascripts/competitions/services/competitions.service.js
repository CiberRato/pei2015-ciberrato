(function () {
    'use strict';

    angular
        .module("ciberonline.competitions.services")
        .factory("Competition", Competition);

    Competition.$inject = ["$cookies", "$http", "$location"];

    function Competition($cookies, $http, $location) {
        var Competition = {
            getAll: getAll,
            getCompetition: getCompetition,
            getTeams: getTeams,
            enroll: enroll,
            deleteEnroll: deleteEnroll

        };

        return Competition;

        function getAll(){
            return $http.get('/api/v1/competitions/crud/');
        }

        function getCompetition(competitionName){
            return $http.get('/api/v1/competitions/crud/' + competitionName +'/');
        }

        function getTeams(competitionName){
            return $http.get('/api/v1/competitions/groups_not_valid/' + competitionName +'/');
        }

        function enroll(competitionName, teamName){
            return $http.post('/api/v1/competitions/enroll/',{
                competition_name: competitionName,
                group_name: teamName
            });
        }

        function deleteEnroll(teamName, competitionName){
            return $http.delete('/api/v1/competitions/enroll/'+ competitionName + '/?group_name=' + teamName);
        }
    }

})();