(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('MyAgentsController', MyAgentsController);

    MyAgentsController.$inject = ['$location', '$route', 'Authentication', 'Agent', 'Team'];

    function MyAgentsController($location, $route, Authentication, Agent) {
        var vm = this;

        vm.deleteAgent = deleteAgent;
        vm.uploadFile = uploadFile;

        activate();

        function activate() {
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            vm.username = authenticatedAccount.username;

            Agent.getByUser(vm.username).then(getByUserSuccessFn, getByUserErrorFn);

            function getByUserSuccessFn(data) {
                vm.agents = data.data;
                console.log(vm.agents);
            }

            function getByUserErrorFn(data) {
                console.error(data.data);
                $location.path("/panel/")
            }

        }

        function deleteAgent(agentName){
            Agent.deleteAgent(agentName).then(deleteAgentSuccessFn, deleteAgentErrorFn);

            function deleteAgentSuccessFn(){
                $.jGrowl("Agent has been removed successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload()
            }

            function deleteAgentErrorFn(data){
                console.error(data.data);
                $.jGrowl("Agent could not be removed.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }

        function uploadFile(name) {

            var language = document.getElementById("selector_language").value;
            console.log(language);
            var selectedFile = document.getElementById('fileupload'+name).files[0];

            if(selectedFile != undefined) {
                Agent.upload(name, language, selectedFile).then(uploadSuccessFn, uploadErrorFn);
            }else{
                $.jGrowl("You didn't select any file", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
            function uploadSuccessFn() {

                $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function uploadErrorFn(data) {
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded:<br>" + data.data.message, {
                    life: 5000,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }

        }

    }
})();