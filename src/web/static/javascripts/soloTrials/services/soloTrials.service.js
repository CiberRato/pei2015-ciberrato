(function () {
    'use strict';

    angular
        .module("ciberonline.soloTrials.services")
        .factory("SoloTrials", SoloTrials);

    SoloTrials.$inject = ['$http'];

    function SoloTrials($http){
        var SoloTrials = {
            getByTeam: getByTeam,
            getAll: getAll
        };

        return SoloTrials;

        function getByTeam(competitionName){
            return $http.get("/api/v1/competitions/private/rounds/" + competitionName + "/");
        }

        function getAll(){
            return $http.get("/api/v1/competitions/private/list/");
        }
    }


})();