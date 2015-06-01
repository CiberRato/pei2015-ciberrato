(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('EditFileController', EditFileController);

    EditFileController.$inject = ['$scope', '$routeParams', 'Agent', 'SoloTrials', '$timeout', 'Notification', '$location'];

    function EditFileController($scope, $routeParams, Agent, SoloTrials, $timeout, Notification, $location){
        var vm = this;
        vm.getCode = getCode;
        vm.getCodeExit = getCodeExit;
        vm.validateCode = validateCode;
        vm.launchTrial = launchTrial;
        var subscribed = false;
        $scope.showLaunch = true;
        $scope.showWait = false;
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
                if(vm.file.substr(vm.file.indexOf('.')) === '.py'){
                    vm.language = "python";
                }else if(vm.file.substr(vm.file.indexOf('.')) === '.java') {
                    vm.language = 'java';
                }else if(vm.file.substr(vm.file.indexOf('.')) === '.xml') {
                    vm.language = 'xml'
                }else if(vm.file.substr(vm.file.indexOf('.')) === '.c' || vm.file.substr(vm.file.indexOf('.')) === '.cpp') {
                    vm.language = 'c_cpp';
                }else if(vm.file.substr(vm.file.indexOf('.')) === '.sh'){
                    vm.language = 'sh';
                }else{
                    vm.language = 'plain_text';
                }
                $scope.aceOptions = {mode: vm.language, theme: 'monokai'};
                Agent.getFile(vm.teamName, vm.agentName, vm.file).then(getFileSuccessFn, getFileErrorFn);

            }

            function getAgentErrorFn(data){
                console.error(data.data);
            }

            function getFileSuccessFn(data){
                $scope.code = data.data;

                SoloTrials.getAll().then(getAllSuccessFn, getAllErrorFn);

                function getAllSuccessFn(data){
                    vm.solos = data.data;
                    console.log(vm.solos);
                    for(var i = 0; i<vm.solos.length; i++){
                        if(vm.solos[i].team == vm.teamName){
                            vm.competitionName = vm.solos[i].competition.name;
                            getCompetitionMaps();
                        }
                    }


                    $scope.loader.loading=true;

                }

                function getAllErrorFn(data){
                    console.error(data.data);
                }

            }

            function getFileErrorFn(data){
                console.error(data.data);
            }

        }

        function getCompetitionMaps(){
            SoloTrials.getByTeam(vm.competitionName).then(getMapsSuccessFn, getMapsErrorFn);

            function getMapsSuccessFn(data){
                vm.maps = data.data;
                console.log(vm.maps);
            }

            function getMapsErrorFn(data){
                console.error(data.data);
            }

        }

        function getCode(){
            var a = $scope.code;

            var file = new Blob([a], {type: 'text/plain'});

            Agent.upload(vm.agentName, file, vm.teamName, vm.file).then(success, error);

            function success(){
                $.jGrowl("File \'" + vm.file + "\' has been updated.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function () {
                    Agent.getAgent(vm.agentName, vm.teamName).then(getAgentSuccessFn, getAgentErrorFn);

                    function getAgentSuccessFn(data) {
                        vm.agent = data.data;
                    }

                    function getAgentErrorFn(data) {
                        console.error(data.data);
                    }
                });
            }
            function error(data){
                console.error(data.data);
            }
        }

        function getCodeExit(){
            var a = $scope.code;

            var file = new Blob([a], {type: 'text/plain'});

            Agent.upload(vm.agentName, file, vm.teamName, vm.file).then(success, error);

            function success(){
                $.jGrowl("File \'" + vm.file + "\' has been updated.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function () {
                    Agent.getAgent(vm.agentName, vm.teamName).then(getAgentSuccessFn, getAgentErrorFn);

                    function getAgentSuccessFn(data) {
                        vm.agent = data.data;
                        $location.path('/panel/' + vm.teamName + '/' + vm.agentName + '/agentDetail')
                    }

                    function getAgentErrorFn(data) {
                        console.error(data.data);
                    }
                });
            }
            function error(data){
                console.error(data.data);
            }
        }

        function validateCode(){
            Agent.validateAgent(vm.agentName, vm.teamName).then(validateSuccessFn, validateErrorFn);

            function validateSuccessFn() {
                $.jGrowl("The code has been submitted for validation!", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });

                if(!subscribed){
                    subscribed = true;
                    console.log("AGENT");
                    var code_validate = Notification.events.subscribe('notificationteam', 1, function(data){

                        if (data.message.trigger == 'code_valid') {
                            $timeout(function () {
                                Agent.getAgent(vm.agentName, vm.teamName).then(getAgentSuccessFn, getAgentErrorFn);

                                function getAgentSuccessFn(data) {
                                    vm.agent = data.data;
                                }

                                function getAgentErrorFn(data) {
                                    console.error(data.data);
                                }
                            });
                        }

                        console.log(data._type);
                        console.log(data.message);
                    });

                    $scope.$on("$destroy", function(event){
                        code_validate.remove();
                    });
                }



            }

            function validateErrorFn(data) {
                console.log(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function launchTrial(){
            var name = document.getElementById("select").value;
            console.log(name);
            SoloTrials.launchTrial(name).then(launchSuccessFn, launchErrorFn);

            function launchSuccessFn(data){
                $.jGrowl("Trial has been created successfully", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                console.log("TRIALS");
                if(!subscribed){
                    subscribed = true;
                    var round_notification = Notification.events.subscribe('notificationteam', 1, function(data){
                        console.log(data);

                        if (data.message.trigger == 'trial_started'){
                            $timeout(function () {
                                $scope.showLaunch = false;
                                $scope.showWait = true;
                            });
                        }

                        if(data.message.trigger == 'trial_log' || data.message.trigger == 'trial_error'){
                            $timeout(function() {
                                $location.path('/panel/trials/'+ name);
                            });
                        }

                        console.log(data._type);
                        console.log(data.message);
                    });
                    console.log(round_notification);
                    $scope.$on("$destroy", function(event){
                        round_notification.remove();
                    });
                }
            }

            function launchErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

    }
})();


