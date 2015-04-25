(function () {
    'use strict';

    angular
        .module('ciberonline.grid.controllers')
        .controller('MyGridsController', MyGridsController);

    MyGridsController.$inject = ['$location', '$timeout', 'Authentication', 'Grid', 'Agent', 'Competition'];

    function MyGridsController($location, $timeout, Authentication, Grid, Agent, Competition){
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

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            vm.username = authenticatedAccount.username;
            Grid.getMyGrids().then(getSuccessFn, getErrorFn);

            function getSuccessFn(data){
                vm.grids = data.data;
                console.log(vm.grids);
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
                    theme: 'success'
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
                    theme: 'btn-danger'
                });
            }
        }

        function getAgents(){
            Agent.getByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);
            Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);


        }

        function getByTeamSuccessFn(data){
            vm.models.lists.Available = [];
            for (var i = 0; i < data.data.length; ++i) {
                vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
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
                    theme: 'success'
                });
                Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);

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
                    theme: 'success'
                });
                Agent.getByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);

                function getByTeamSuccessFn(data){
                    vm.models.lists.Available = [];
                    for (var i = 0; i < data.data.length; ++i) {
                        vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                    }
                    console.log(vm.models.lists.Available);
                    Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);


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
                    theme: 'btn-danger'
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
                        Grid.disassociateAgent(vm.identifier, vm.models.lists.GridPosition[j].pos);
                    }
                    console.log(vm.models.lists.GridPosition);

                    for(var k= 0; k<vm.models.lists.GridPosition.length; k++){
                        gridAssociate(vm.models.lists.GridPosition[k].label, k+1, teamName);
                    }
                    console.log(vm.models.lists.GridPosition);
                    Grid.getAgents(vm.identifier).then(getAssociatedAgentsSuccessFn, getAssociatedAgentsErrorFn);

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

        function gridAssociate(agent_name, pos, teamName){
            Grid.associateAgent(agent_name, vm.identifier, pos, teamName).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getByTeam(vm.team).then(getByTeamSuccessFn, getByTeamErrorFn);
            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }
        }

    }
})();