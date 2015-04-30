(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('EditFileController', EditFileController);

    EditFileController.$inject = ['$scope', '$routeParams', 'Authentication', 'Agent', 'Team'];

    function EditFileController($scope, $routeParams, Authentication, Agent, Team){
        var vm = this;
        activate();

        function activate(){
            vm.teamName = $routeParams.teamName;
            vm.agentName = $routeParams.name;
            vm.file = $routeParams.fileName;

            Agent.getFile(vm.teamName, vm.agentName, vm.file).then(getFileSuccessFn, getFileErrorFn);

            function getFileSuccessFn(data){
                console.log(data.data);
                $scope.code = data.data;
            }

            function getFileErrorFn(data){
                console.error(data.data);
            }

        }

    }
})();


