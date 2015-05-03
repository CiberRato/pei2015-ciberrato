(function () {
    'use strict';

    angular
        .module("ciberonline.soloTrials.services")
        .factory("SoloTrials", SoloTrials);

    SoloTrials.$inject = ['$http'];

    function SoloTrials($http){
        var SoloTrials = {
            getByTeam: getByTeam,
            getAll: getAll,
            create: create
        };

        return SoloTrials;

        function getByTeam(competitionName){
            return $http.get("/api/v1/competitions/private/rounds/" + competitionName + "/");
        }

        function getAll(){
            return $http.get("/api/v1/competitions/private/list/");
        }

        function create(competitionName, grid, lab, param){
            return $http.post("/api/v1/competitions/private/create_round/", {
                competition_name: competitionName,
                grid: grid,
                lab: lab,
                param_list: param
            });
        }
    }


})();