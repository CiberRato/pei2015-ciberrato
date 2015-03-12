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
            getNotValidTeams: getNotValidTeams,
            enroll: enroll

        };

        return Competition;

        function getAll(){
            return $http.get('/api/v1/competitions/crud/');
        }

        function getCompetition(competitionName){
            return $http.get('/api/v1/competitions/crud/' + competitionName +'/');
        }

        function getNotValidTeams(competitionName){
            return $http.get('/api/v1/competitions/groups_not_valid/' + competitionName +'/');
        }

        function enroll(competitionName, teamName){
            return $http.post('/api/v1/competitions/enroll/',{
                competition_name: competitionName,
                group_name: teamName
            });
        }
    }

})();