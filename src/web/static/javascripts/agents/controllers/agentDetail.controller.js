(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$routeParams', '$scope', '$route', 'Agent', 'Competition'];

    function AgentDetailController($location, $routeParams, $scope, $route,  Agent, Competition) {
        var vm = this;
        vm.uploadFile = uploadFile;
        vm.deleteUpload = deleteUpload;
        vm.associate = associate;
        var agentName = $routeParams.name;

        activate();

        function activate() {
            Agent.getAgent(agentName).then(getAgentSuccessFn, getAgentErrorFn);
            Agent.getFiles(agentName).then(getFilesSuccessFn, getFilesErrorFn);


            function getAgentSuccessFn(data, status, headers, config) {
                vm.agent = data.data;
                console.log(vm.agent);
                Competition.getCompetitions(vm.agent.group_name).then(getCompetitionsSuccessFn, getCompetitionsErrorFn);


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

            function getCompetitionsSuccessFn(data){
                vm.competitions = data.data;
                console.log(vm.competitions);
            }

            function getCompetitionsErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function uploadFile() {
            var language = document.getElementById("selector_language").value;
            var selectedFile = document.getElementById('fileupload').files[0];

            Agent.upload(agentName, language, selectedFile).then(uploadSuccessFn, uploadErrorFn);

            function uploadSuccessFn(){

                $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function uploadErrorFn(data){
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.log(data.data);
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
                console.log(data.data);
            }

        }

        function associate(){
            var competitionName = document.getElementById("selector_agent").value;
            Competition.getFirstRound(competitionName).then(getFirstRoundSuccessFn, getFirstRoundErrorFn);

            function getFirstRoundSuccessFn(data){
                vm.round  = data;
                Agent.associate(competitionName, agentName).then(associateSuccessFn, associateErrorFn);

                function associateSuccessFn(){
                    $.jGrowl("Agent \'" + agentName + "\' has been associated.", {
                        life: 2500,
                        theme: 'success'
                    });
                    $route.reload();
                }

                function associateErrorFn(data){
                    console.error(data.data);
                    $.jGrowl("Agent \'" + agentName + "\' can't be associated twice to one competition.", {
                        life: 2500,
                        theme: 'btn-danger'
                    });
                }
            }

            function getFirstRoundErrorFn(data){
                console.error(data.data);
                $location.path("/panel/");
            }

        }

    }

})();
