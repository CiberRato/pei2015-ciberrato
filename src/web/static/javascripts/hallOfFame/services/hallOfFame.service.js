(function () {
    'use strict';

    angular
        .module("ciberonline.hallOfFame.services")
        .factory("HallOfFame", HallOfFame);

    HallOfFame.$inject = ["$http"];

    function HallOfFame($http) {
        var HallOfFame = {
            create: create

        };

        return HallOfFame;

        function create(competitionName, roundName, param, file) {
            return $http.post("/api/v1/set_round_file/" + competitionName + "/" + roundName + "/" + param + "/", {
                path: file
            })
        }


    }

})();