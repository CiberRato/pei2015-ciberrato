(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$routeParams', '$route', 'Agent'];

    function AgentDetailController($location, $routeParams, $route,  Agent) {
        var vm = this;
        vm.uploadFile = uploadFile;
        vm.deleteUpload = deleteUpload;
        var agentName = $routeParams.name;

        activate();

        function activate() {
            Agent.getAgent(agentName).then(getAgentSuccessFn, getAgentErrorFn);
            Agent.getFiles(agentName).then(getFilesSuccessFn, getFilesErrorFn);

            function getAgentSuccessFn(data) {
                vm.agent = data.data;

            }

            function getAgentErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');
            }

            function getFilesSuccessFn(data) {
                vm.files = data.data;
                console.log(vm.files);

            }

            function getFilesErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');
            }

        }

        function uploadFile() {
            var selectedFile = document.getElementById('fileupload').files;
            if(selectedFile.length == 0){
                $.jGrowl("You didn't select any file", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }else{
                for(var i = 0; i< selectedFile.length; i++) {
                    uploadCode(selectedFile[i]);
                }
            }


            function uploadCode(selectedFile){
                Agent.upload(agentName, selectedFile).then(uploadSuccessFn, uploadErrorFn);

                function uploadSuccessFn() {

                    $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                        life: 2500,
                        theme: 'success'
                    });
                    $route.reload();
                }

                function uploadErrorFn(data) {
                    console.log(data.data);
                    $.jGrowl(data.data.message, {
                        life: 2500,
                        theme: 'btn-danger'
                    });
                }
            }


        }

        function deleteUpload(fileName) {
            Agent.deleteUpload(agentName, fileName).then(deleteUploadSuccessFn, deleteUploadErrorFn);

            function deleteUploadSuccessFn() {
                $.jGrowl("File \'" + fileName + "\' has been deleted.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();

            }

            function deleteUploadErrorFn(data) {
                $.jGrowl("File \'" + fileName + "\' can't be deleted.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }

        }

    }

})();
