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

        function getLabViewer(RoundName){
            return $http.get('/api/v1/competitions/round_file/' + RoundName + '/?file=lab');
        }

        function getParametersViewer(RoundName){
            return $http.get('/api/v1/competitions/round_file/' + RoundName + '/?file=param_list');
        }

        function getGridViewer(RoundName){
            return $http.get('/api/v1/competitions/round_file/' + RoundName + '/?file=grid');
        }

    }
})();