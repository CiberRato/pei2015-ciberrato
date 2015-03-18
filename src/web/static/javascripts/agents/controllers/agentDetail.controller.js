(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$routeParams', '$scope', 'Agent'];

    function AgentDetailController($location, $routeParams, $scope, Agent) {
        var vm = this;
        vm.uploadFile = uploadFile;
        vm.deleteUpload = deleteUpload;
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
                console.log(vm.files);


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

        function deleteUpload(fileName){
            Agent.deleteUpload(agentName, fileName).then(deleteUploadSuccessFn, deleteUploadErrorFn);

            function deleteUploadSuccessFn(){
                $.jGrowl("File \'" + fileName +"\' has been deleted.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/panel/'+agentName+'/agentDetail');
            }

            function deleteUploadErrorFn(data){
                $.jGrowl("File \'" + fileName +"\' can't be deleted.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.log(data.data);
            }
        }






    }

})();
