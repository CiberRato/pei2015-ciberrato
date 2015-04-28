(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$timeout', '$dragon', '$routeParams', '$route', 'Agent'];

    function AgentDetailController($location, $timeout, $dragon, $routeParams, $route,  Agent) {
        var vm = this;
        vm.uploadFile = uploadFile;
        vm.deleteUpload = deleteUpload;
        vm.validateCode = validateCode;
        var agentName = $routeParams.name;
        console.log($routeParams);
        var teamName = $routeParams.teamName;

        activate();

        function activate() {
            Agent.getAgent(agentName, teamName).then(getAgentSuccessFn, getAgentErrorFn);
            Agent.getFiles(agentName, teamName).then(getFilesSuccessFn, getFilesErrorFn);

            function getAgentSuccessFn(data) {
                vm.agent = data.data;
                console.log(vm.agent);

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

        function validateCode(){
            Agent.validateAgent(agentName, teamName).then(validateSuccessFn, validateErrorFn);

                function validateSuccessFn() {
                    $.jGrowl("The code has been submitted for validation!", {
                        life: 2500,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                    });
                    $dragon.onReady(function() {
                        swampdragon.open(function () {
                            $dragon.onChannelMessage(function(channels, data) {
                                /*
                                 if (data.data.message.status == 200){
                                 $.jGrowl(data.data.message.content, {
                                 life: 3500,
                                 theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                                 });
                                 }else if(data.data.message.status == 400){
                                 $.jGrowl(data.data.message.content, {
                                 life: 3500,
                                 theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                                 });
                                 }
                                 */
                                if (data.data.message.trigger == 'code_valid'){
                                    $timeout(function(){
                                        Agent.getAgent(agentName, teamName).then(getAgentSuccessFn, getAgentErrorFn);

                                        function getAgentSuccessFn(data) {
                                            vm.agent = data.data;
                                        }

                                        function getAgentErrorFn(data) {
                                            console.error(data.data);
                                        }
                                    });
                                }
                                console.log(channels);
                                console.log(data.data._type);
                                console.log(data.data.message);
                            });
                        });
                    });

                }



                function validateErrorFn(data) {
                    console.log(data.data);
                    $.jGrowl(data.data.message, {
                        life: 2500,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                    });
                }
        }

        function uploadFile() {
            var selectedFile = document.getElementById('fileupload').files;
            if(selectedFile.length == 0){
                $.jGrowl("You didn't select any file", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }else{
                for(var i = 0; i< selectedFile.length; i++) {
                    uploadCode(selectedFile[i]);
                }
            }


            function uploadCode(selectedFile){
                Agent.upload(agentName, selectedFile, teamName).then(uploadSuccessFn, uploadErrorFn);

                function uploadSuccessFn() {

                    $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                        life: 2500,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                    });
                    $timeout(function(){
                        getFiles();
                    });
                }

                function uploadErrorFn(data) {
                    console.log(data.data);
                    $.jGrowl(data.data.message, {
                        life: 2500,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                    });
                }
            }


        }

        function deleteUpload(fileName) {
            Agent.deleteUpload(agentName, fileName, teamName).then(deleteUploadSuccessFn, deleteUploadErrorFn);

            function deleteUploadSuccessFn() {
                $.jGrowl("File \'" + fileName + "\' has been deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    getFiles();
                    vm.agent.validation_result = [];

                });

            }

            function deleteUploadErrorFn(data) {
                $.jGrowl("File \'" + fileName + "\' can't be deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                console.error(data.data);
            }

        }

        function getFiles(){
            Agent.getFiles(agentName, teamName).then(getFilesSuccessFn, getFilesErrorFn);

            function getFilesSuccessFn(data) {
                vm.files = data.data;
                console.log(vm.files);

            }

            function getFilesErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');
            }

        }

    }

})();
