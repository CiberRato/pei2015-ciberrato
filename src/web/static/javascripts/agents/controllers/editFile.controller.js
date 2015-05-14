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
            $scope.loader = {
                loading: false
            };
            vm.teamName = $routeParams.teamName;
            vm.agentName = $routeParams.name;
            vm.file = $routeParams.fileName;
            Agent.getAgent(vm.agentName, vm.teamName).then(getAgentSuccessFn, getAgentErrorFn);

            function getAgentSuccessFn(data){
                vm.agent = data.data;
                console.log(vm.file.substr(vm.file.indexOf('.')))
                if(vm.file.substr(vm.file.indexOf('.')) === '.py'){
                    vm.language = "python";
                }else if(vm.file.substr(vm.file.indexOf('.')) === '.java'){
                    vm.language = 'java';
                }else if(vm.file.substr(vm.file.indexOf('.')) === '.c' || vm.file.substr(vm.file.indexOf('.')) === '.cpp') {
                    vm.language = 'c_cpp';
                }else if(vm.file.substr(vm.file.indexOf('.')) === '.sh'){
                    vm.language = 'sh';
                }else{
                    vm.language = 'plain_text';
                }
                console.log(vm.language);
                $scope.aceOptions = {mode: vm.language, theme: 'monokai'};
                Agent.getFile(vm.teamName, vm.agentName, vm.file).then(getFileSuccessFn, getFileErrorFn);

            }

            function getAgentErrorFn(data){
                console.error(data.data);
            }

            function getFileSuccessFn(data){
                $scope.code = data.data;
                $scope.loader.loading=true;


            }

            function getFileErrorFn(data){
                console.error(data.data);
            }

        }

        function getCode(){
            var a = $scope.code;
            console.log(a);

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


