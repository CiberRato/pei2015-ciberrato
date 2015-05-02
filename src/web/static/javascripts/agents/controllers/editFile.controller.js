(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('EditFileController', EditFileController);

    EditFileController.$inject = ['$scope', '$routeParams', 'Authentication', 'Agent', 'Team'];

    function EditFileController($scope, $routeParams, Authentication, Agent, Team){
        var vm = this;
        vm.getCode = getCode;
        activate();

        function activate(){
            vm.teamName = $routeParams.teamName;
            vm.agentName = $routeParams.name;
            vm.file = $routeParams.fileName;
            Agent.getAgent(vm.agentName, vm.teamName).then(getAgentSuccessFn, getAgentErrorFn);

            function getAgentSuccessFn(data){
                vm.agent = data.data;
                if(vm.agent.language === 'Python'){
                    vm.language = "python";
                }else if(vm.agent.language === 'Java'){
                    vm.language = 'java';
                }else if(vm.agent.language === 'C' || vm.agent.language === 'C++'){
                    vm.language = 'c_cpp';
                }else{
                    vm.language = 'plain_text';
                }
                console.log(vm.language);
                Agent.getFile(vm.teamName, vm.agentName, vm.file).then(getFileSuccessFn, getFileErrorFn);

            }

            function getAgentErrorFn(data){
                console.error(data.data);
            }

            function getFileSuccessFn(data){
                console.log(data.data);

                $scope.code = data.data;
            }

            function getFileErrorFn(data){
                console.error(data.data);
            }

        }

        function getCode(){
            var a = $scope.code;
            var file = new Blob([a], {type: 'text/plain'});

            Agent.upload(vm.agentName, file, vm.teamName, vm.file).then(success, error);

            function success(){
                console.log("UPLOADDD")
            }
            function error(data){
                console.error(data.data);
            }
        }

    }
})();


