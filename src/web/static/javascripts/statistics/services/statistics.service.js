(function () {
    'use strict';

    angular
        .module("ciberonline.statistics.services")
        .factory("Statistics", Statistics);

    Statistics.$inject = ['$http'];

    function Statistics($http){
        var Statistics = {
            getStats: getStats
        };

        return Statistics;

        function getStats(){
            return $http.get("/api/v1/statistics/media/");
        }
    }


})();