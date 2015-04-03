(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$routeParams', '$route', 'Agent', 'Competition'];

    function AgentDetailController($location, $routeParams, $route,  Agent, Competition) {
        var vm = this;
        vm.uploadFile = uploadFile;
        vm.deleteUpload = deleteUpload;
        vm.associate = associate;
        var agentName = $routeParams.name;

        activate();

        function activate() {
            Agent.getAgent(agentName).then(getAgentSuccessFn, getAgentErrorFn);
            Agent.getFiles(agentName).then(getFilesSuccessFn, getFilesErrorFn);
            Agent.getLanguages().then(getLanguagesSuccessFn, getLanguagesErrorFn);


            function getAgentSuccessFn(data) {
                vm.agent = data.data;
                Competition.getCompetitions(vm.agent.group_name).then(getCompetitionsSuccessFn, getCompetitionsErrorFn);


            }

            function getAgentErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');
            }

            function getFilesSuccessFn(data) {
                vm.files = data.data;

            }

            function getFilesErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');
            }

            function getCompetitionsSuccessFn(data){
                vm.competitions = data.data;
            }

            function getCompetitionsErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getLanguagesSuccessFn(data){
                vm.languages = data.data;
            }

            function getLanguagesErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function uploadFile() {
            var language = document.getElementById("selector_language").value;
            console.log(language);
            var selectedFile = document.getElementById('fileupload').files[0];

            if(selectedFile != undefined) {
                Agent.upload(agentName, language, selectedFile).then(uploadSuccessFn, uploadErrorFn);
            }
            function uploadSuccessFn() {

                $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function uploadErrorFn(data) {
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
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
                    Competition.getCompetitions(vm.agent.group_name).then(getCompetitionsSuccessFn, getCompetitionsErrorFn);
                    $route.reload();
                }

                function associateErrorFn(data){
                    console.error(data.data);
                    $.jGrowl("Agent \'" + agentName + "\' can't be associated to the competition.", {
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
