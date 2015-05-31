(function () {
    'use strict';

    angular
        .module("ciberonline.logviewer.services")
        .factory("LogViewer", LogViewer);

    LogViewer.$inject = ['$http'];

    function LogViewer($http){
        var logViewer = {
            getLog: getLog,
            getExecutionLog: getExecutionLog
        };

        return logViewer;

        function getLog(identifier){
            return $http.get('/api/v1/trials/get_trial_log/'+identifier+'/');
        }

        function getExecutionLog(identifier){
            return $http.get('/api/v1/trials/execution_log/' + identifier + '/');
        }
    }
})();

