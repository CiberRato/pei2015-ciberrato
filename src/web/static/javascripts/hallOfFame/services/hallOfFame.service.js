(function () {
    'use strict';

    angular
        .module("ciberonline.hallOfFame.services")
        .factory("HallOfFame", HallOfFame);

    HallOfFame.$inject = ["$http"];

    function HallOfFame($http) {
        var HallOfFame = {
            createGrid: createGrid,
            createLab: createLab,
            createParam: createParam

        };

        return HallOfFame;

        function createGrid(competitionName, roundName, param, file){
            return $http.post("/api/v1/set_round_file/" + competitionName + "/" + roundName + "/" +  param + "/", {
                path: file
            })
        }
        function createLab(competitionName, roundName, param, file){
            return $http.post("/api/v1/set_round_file/" + competitionName + "/" + roundName + "/" +  param + "/", {
                path: file
            })
        }
        function createParam(competitionName, roundName, param, file){
            return $http.post("/api/v1/set_round_file/" + competitionName + "/" + roundName + "/" +  param + "/", {
                path: file
            })
        }


    }

})();