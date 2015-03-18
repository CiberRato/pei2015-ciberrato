(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$routeParams', '$scope', 'Agent'];

    function AgentDetailController($location,$routeParams, $scope, Agent) {
        var vm = this;
        vm.uploadFile = uploadFile;
        var agentName = $routeParams.name;

        console.log($scope.files);
        activate();

        function activate() {
            Agent.getAgent(agentName).then(getAgentSuccessFn, getAgentErrorFn);
            Agent.getFiles(agentName).then(getFilesSuccessFn, getFilesErrorFn);

            function getAgentSuccessFn(data, status, headers, config) {
                vm.agent = data.data;

            }

            function getAgentErrorFn(data, status, headers, config) {
                console.error(data.data);
                $location.url('/panel/');
            }

            function getFilesSuccessFn(data, status, headers, config) {
                vm.files = data.data;


            }

            function getFilesErrorFn(data, status, headers, config) {
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function uploadFile() {
            var language = document.getElementById("selector_language").value;
            var selectedFile = document.getElementById('fileupload').files[0];

            Agent.upload(agentName, language, selectedFile);

        }






    }

})();
