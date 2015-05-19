(function () {
    'use strict';

    angular
        .module("ciberonline.hallOfFame.services")
        .factory("HallOfFame", HallOfFame);

    HallOfFame.$inject = ["$http"];

    function HallOfFame($http) {
        var HallOfFame = {
            create: create,
            launchTrial: launchTrial

        };

        return HallOfFame;

        function create(competitionName, roundName, param, file) {
            return $http.post("/api/v1/set_round_file/" + competitionName + "/" + roundName + "/" + param + "/", {
                path: file
            });
        }

        function launchTrial(roundName, agentName, team){
            return $http.post("/api/v1/competitions/hall_of_fame/launch_trial/", {
                round_name: roundName,
                agent_name: agentName,
                team_name: team
            });
        }


    }

})();