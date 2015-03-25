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
                    var tmp = data.split("&");
                    for(var i=0; i<tmp.length; i++){
                        tmp[i] = angular.fromJson(tmp[i]);
                    }
                    return tmp;
                }]
            });
        }
    }
})();

