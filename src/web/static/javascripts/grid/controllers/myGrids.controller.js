(function () {
    'use strict';

    angular
        .module('ciberonline.grid.controllers')
        .controller('MyGridsController', MyGridsController);

    MyGridsController.$inject = ['$location', '$timeout', 'Authentication', 'Grid', 'Agent', 'Competition', '$scope'];

    function MyGridsController($location, $timeout, Authentication, Grid, Agent, Competition, $scope){
        var vm = this;
        vm.username;
        vm.models = {
            selected: null,
            lists: {"Available": [], "GridPosition": []}
        };

        vm.destroy = destroy;
        vm.getAgents = getAgents;
        vm.associate = associate;
        vm.disassociate = disassociate;
        vm.getCompetition = getCompetition;
        vm.number = [];
        vm.associateAllRemote = associateAllRemote;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            vm.username = authenticatedAccount.username;
            Grid.getMyGrids().then(getSuccessFn, getErrorFn);

            function getSuccessFn(data){
                vm.grids = data.data;
                console.log(vm.grids);
                $scope.loader = {
                    loading: true
                };
            }

            function getErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

        }

        function destroy(teamName, competitionName){
            Grid.destroy(teamName, competitionName).then(destroySuccessFn, destroyErrorFn);

            function destroySuccessFn(){
                $.jGrowl("Grid Position has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function() {
                    Grid.getMyGrids().then(getSuccessFn, getErrorFn);

                    function getSuccessFn(data) {
                        vm.grids = data.data;
                        console.log(vm.grids);
                    }

                    function getErrorFn(data) {
                        console.error(data.data);
                        $location.url('/panel/');
                    }
                });
            }

            function destroyErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function getAgents(){
            Agent.getValidByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);
            Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);


        }

        function getByTeamSuccessFn(data){
            vm.models.lists.Available = [];
            for (var i = 0; i < data.data.length; ++i) {
                if(data.data[i].agent_name === "Remote" && vm.competition.allow_remote_agents === true){
                    vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                }else if(data.data[i].agent_name !== "Remote"){
                    vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                }
            }

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
            Grid.associateAgent(agent_name, vm.identifier, pos, teamName).then(associateSuccessFn, associateErrorFn);

            function associateSuccessFn(){
                $.jGrowl("Agent has been associated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateErrorFn(data){
                console.error(data.data);
            }

        }

        function disassociate(pos, teamName){
            Grid.disassociateAgent(vm.identifier, pos, teamName).then(disassociateSuccessFn, disassociateErrorFn);
            console.log(vm.models.lists.GridPosition);
            function disassociateSuccessFn(){
                $.jGrowl("Agent has been disassociated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                Agent.getValidByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);

                function getByTeamSuccessFn(data){
                    vm.models.lists.Available = [];
                    for (var i = 0; i < data.data.length; ++i) {
                        if(data.data[i].agent_name === "Remote" && vm.competition.allow_remote_agents === true){
                            vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                        }else if(data.data[i].agent_name !== "Remote"){
                            vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                        }
                    }
                    console.log(vm.models.lists.Available);
                    Grid.getAgents(vm.identifier).then(getAssociatedAgentsSuccessFn, getAssociatedAgentsErrorFn);


                }

                function getByTeamErrorFn(data){
                    console.error(data.data);
                    $location.url('/panel/');

                }

            }

            function disassociateErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }

            function getAssociatedAgentsSuccessFn(data){
                vm.models.lists.GridPosition = [];
                for (var i = 0; i < data.data.length; ++i) {
                    vm.models.lists.GridPosition.push({label: data.data[i].agent_name, pos: data.data[i].position});
                }
                console.log(vm.models.lists.GridPosition);
                if(vm.models.lists.GridPosition !== []){
                    for(var j = 0; j<vm.models.lists.GridPosition.length; j++){
                        gridDisassociate(vm.models.lists.GridPosition[j].pos);
                    }
                    vm.tmp = vm.models.lists.GridPosition;
                    Grid.getAgents(vm.identifier).then(getAssociatedNSuccessFn, getAssociatedNErrorFn);

                }

                function getAssociatedNSuccessFn(){
                    console.log(vm.models.lists.GridPosition);
                    for(var k= 0; k<vm.tmp.length; k++){
                        gridAssociate(vm.tmp[k].label, k+1, teamName);
                    }
                    console.log(vm.models.lists.GridPosition);
                    Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                }

                function getAssociatedNErrorFn(data){
                    console.error(data.data);
                }

            }

            function getAssociatedAgentsErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');

            }
        }

        function getCompetition(competitionName){
            Competition.getCompetition(competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);

            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
            }

            function getCompetitionErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');

            }
        }

        function gridDisassociate(pos){
            Grid.disassociateAgent(vm.identifier, pos).then(disassociateSuccessFn, disassociateErrorFn);

            function disassociateSuccessFn(){
                console.log("desassociei" + pos);
            }

            function disassociateErrorFn(data){
                console.error(data.data);
            }
        }

        function gridAssociate(agent_name, pos, teamName){
            Grid.associateAgent(agent_name, vm.identifier, pos, teamName).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                console.log("associei" + agent_name + pos);
                Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }
        }

        function associateAllRemote(){
            console.log(vm.models.lists.GridPosition.length);
            for(var i = vm.models.lists.GridPosition.length; i<vm.competition.type_of_competition.number_agents_by_grid; i++){
                associateRemote(i+1);
            }
        }

        function associateRemote(i){
            Grid.associateAgent("Remote", vm.identifier, i, vm.team).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                $.jGrowl("Agent has been associated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }

        }

    }
})();