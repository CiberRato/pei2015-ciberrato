(function () {
    'use strict';

    angular
        .module("ciberonline.logviewer.services")
        .factory("LogViewer", LogViewer);

    LogViewer.$inject = ['$http'];

    function LogViewer($http){
        var logViewer = {
            getLog: getLog
        };

        return logViewer;

        function getLog(identifier){
            return $http({
                url: '/api/v1/competitions/get_simulation_log/'+identifier+'/',
                method: 'GET',
                transformResponse: [function (data) {
                    return angular.fromJson(data);
                }]
            });
        }
    }
})();

