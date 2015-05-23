(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('SoloByUserController', SoloByUserController);

    SoloByUserController.$inject = ['SoloTrials', '$scope', 'Round', 'Grid', 'Agent', '$location'];

    function SoloByUserController(SoloTrials, $scope, Round, Grid, Agent, $location){
        var vm = this;
        vm.models = {
            selected: null,
            lists: {"Available": [], "GridPosition": []}
        };

        vm.associate = associate;
        vm.disassociate = disassociate;
        vm.getGrid = getGrid;


        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            SoloTrials.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.solos = data.data;
                console.log(vm.solos);
                Round.getResources().then(success, error);

                function success(data){
                    vm.resources = data.data;
                    console.log(vm.resources);
                    $scope.loader = {
                        loading: true
                    };
                }

                function error(data){
                    console.error(data.data);
                }
            }


            function getAllErrorFn(data){
                console.error(data.data);
            }


        }

        function getGrid(teamName, competitionName){
            vm.tmp1 = false;
            Grid.getGrid(teamName, competitionName).then(success, error);

            function success(data){
                console.log(data.data);
                vm.grid = data.data;
                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);


            }

            function error(data){
                console.error(data.data);
            }
        }

        function getByTeamSuccessFn(data) {
            vm.models.lists.Available = [];
            for (var i = 0; i < data.data.length; ++i) {
                vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
            }
            if(vm.models.lists.Available.length == 0){
                vm.tmp1 = true;
            }
            console.log(vm.grid.identifier);
            Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
        }

        function getByTeamErrorFn(data){
            console.error(data.data);
            $location.url('/panel/');

        }

        function getAssociatedSuccessFn(data){
            vm.models.lists.GridPosition = [];
            for (var i = 0; i < data.data.length; ++i) {
                vm.models.lists.GridPosition.push({label: data.data[i].agent_name, pos: data.data[i].position, type: 'Grid'});
            }
        }

        function getAssociatedErrorFn(data){
            console.error(data.data);
            $location.url('/panel/');

        }

        function associate(agent_name, teamName){
            console.log(vm.models.lists);

            var pos = vm.models.lists.GridPosition.length;
            console.log(teamName);
            Grid.associateAgent(agent_name, vm.grid.identifier, pos, teamName).then(associateSuccessFn, associateErrorFn);

            function associateSuccessFn(){
                $.jGrowl("Agent has been associated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateErrorFn(data){
                console.error(data.data);
            }

        }

        function disassociate(pos, teamName) {
            Grid.disassociateAgent(vm.grid.identifier, pos, teamName).then(disassociateSuccessFn, disassociateErrorFn);
            console.log(vm.models.lists.GridPosition);
            function disassociateSuccessFn() {
                $.jGrowl("Agent has been disassociated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });

                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

                function getByTeamSuccessFn(data) {
                    vm.models.lists.Available = [];
                    for (var i = 0; i < data.data.length; ++i) {

                        vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});

                    }
                    console.log(vm.models.lists.Available);
                    Grid.getAgents(vm.grid.identifier).then(getAssociatedAgentsSuccessFn, getAssociatedAgentsErrorFn);


                }

                function getByTeamErrorFn(data) {
                    console.error(data.data);
                    $location.url('/panel/');

                }

            }

            function disassociateErrorFn(data) {
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }

            function getAssociatedAgentsSuccessFn(data) {
                vm.models.lists.GridPosition = [];
                for (var i = 0; i < data.data.length; ++i) {
                    vm.models.lists.GridPosition.push({label: data.data[i].agent_name, pos: data.data[i].position});
                }
                console.log(vm.models.lists.GridPosition);
                if (vm.models.lists.GridPosition !== []) {
                    for (var j = 0; j < vm.models.lists.GridPosition.length; j++) {
                        gridDisassociate(vm.models.lists.GridPosition[j].pos);
                    }
                    vm.tmp = vm.models.lists.GridPosition;
                    Grid.getAgents(vm.grid.identifier).then(getAssociatedNSuccessFn, getAssociatedNErrorFn);

                }

                function getAssociatedNSuccessFn() {
                    console.log(vm.models.lists.GridPosition);
                    for (var k = 0; k < vm.tmp.length; k++) {
                        gridAssociate(vm.tmp[k].label, k + 1, teamName);
                    }
                    console.log(vm.models.lists.GridPosition);
                    Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                }

                function getAssociatedNErrorFn(data) {
                    console.error(data.data);
                }

            }

            function getAssociatedAgentsErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');

            }
        }

        function gridDisassociate(pos){
            Grid.disassociateAgent(vm.grid.identifier, pos).then(disassociateSuccessFn, disassociateErrorFn);

            function disassociateSuccessFn(){
                console.log("desassociei" + pos);
            }

            function disassociateErrorFn(data){
                console.error(data.data);
            }
        }

        function gridAssociate(agent_name, pos, teamName){
            Grid.associateAgent(agent_name, vm.grid.identifier, pos, teamName).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                console.log("associei" + agent_name + pos);

                Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }
        }



    }

})();