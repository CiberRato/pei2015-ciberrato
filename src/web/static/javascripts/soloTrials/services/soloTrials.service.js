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
            create: create,
            getTrials: getTrials,
            launchTrial: launchTrial,
            removeTrial: removeTrial,
            removeSoloTrial: removeSoloTrial
        };

        return SoloTrials;

        function getByTeam(competitionName){
            return $http.get("/api/v1/competitions/private/rounds/" + competitionName + "/");
        }

        function getAll(){
            return $http.get("/api/v1/competitions/private/list/");
        }

        function create(competitionName, grid, lab, param){
            return $http.post("/api/v1/competitions/private/round/", {
                competition_name: competitionName,
                grid: grid,
                lab: lab,
                param_list: param
            });
        }

        function getTrials(roundName){
            return $http.get("/api/v1/competitions/private/round/" + roundName + "/");
        }

        function launchTrial(roundName){
            return $http.post("/api/v1/competitions/private/launch_trial/", {
                round_name: roundName
            });
        }

        function removeTrial(identifier){
            return $http.delete("/api/v1/competitions/private/trial/" + identifier + "/");
        }

        function removeSoloTrial(name){
            return $http.delete("/api/v1/competitions/private/round/" + name + "/");
        }
    }


})();