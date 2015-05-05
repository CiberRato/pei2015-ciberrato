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
            getGridViewer: getGridViewer
        };

        return streamViewer;

        function getLabViewer(RoundName, CompetitionName){
            return $http.get('/api/v1/competitions/round_json_file/' + CompetitionName + '/' + RoundName + '/lab/');
        }

        function getParametersViewer(RoundName, CompetitionName){
            return $http.get('/api/v1/competitions/round_json_file/' + CompetitionName + '/' + RoundName + '/param_list/');
        }

        function getGridViewer(RoundName, CompetitionName){
            return $http.get('/api/v1/competitions/round_json_file/' + CompetitionName + '/' + RoundName + '/grid/');
        }

    }
})();