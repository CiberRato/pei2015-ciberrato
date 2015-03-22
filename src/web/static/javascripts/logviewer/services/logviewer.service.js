(function () {
    'use strict';

    angular
        .module("ciberonline.logviewer.services")
        .factory("LogViewer", LogViewer);

    LogViewer.$inject = ['$http'];

    function LogViewer($http){
        var logViewer = {
            getLabViewer: getLabViewer,
            getParametersViewer: getParametersViewer,
            getGridViewer: getGridViewer,
            getLogViewer: getLogViewer
        };

        return logViewer;

        function getLabViewer(){
            return $http.get('media/tests_files/logs/lab_json.txt');
        }

        function getParametersViewer(){
            return $http.get('media/tests_files/logs/parameters_json.txt');
        }

        function getGridViewer(){
            return $http.get('media/tests_files/logs/grid_json.txt');
        }

        function getLogViewer(){
            return $http.get('media/tests_files/logs/log_json.txt');
        }
    }
})();

