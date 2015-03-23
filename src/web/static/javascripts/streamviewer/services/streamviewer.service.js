(function () {
    'use strict';

    angular
        .module("ciberonline.streamviewer.services")
        .factory("StreamViewer", StreamViewer);

    StreamViewer.$inject = ['$http'];

    function StreamViewer($http){
        var streamViewer = {
            getLabViewer: getLabViewer,
            getParametersViewer: getParametersViewer,
            getGridViewer: getGridViewer,
            getLogViewer: getLogViewer
        };

        return streamViewer;

        function getLabViewer(){
            return $http.get('media/tests_files/logs/lab_stream.txt');
        }

        function getParametersViewer(){
            return $http.get('media/tests_files/logs/param_stream.txt');
        }

        function getGridViewer(){
            return $http.get('media/tests_files/logs/grid_stream.txt');
        }

        function getLogViewer(){
            return $http.get('media/tests_files/logs/log_json.txt');
        }
    }
})();