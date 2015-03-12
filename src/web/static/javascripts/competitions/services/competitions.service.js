(function () {
    'use strict';

    angular
        .module("ciberonline.competitions.services")
        .factory("Competition", Competition);

    Competition.$inject = ["$cookies", "$http", "$location"];

    function Competition($cookies, $http, $location) {
        var Competition = {
            getAll: getAll

        };

        return Competition;

        function getAll(){
            return $http.get('/api/v1/competitions/crud/');
        }
    }

})();