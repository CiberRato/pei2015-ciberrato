(function () {
    'use strict';

    angular
        .module('ciberonline.grid.controllers')
        .controller('MyGridsController', MyGridsController);

    MyGridsController.$inject = ['$location', '$route', 'Authentication', 'Grid', 'Agent', 'Competition'];

    function MyGridsController($location, $route, Authentication, Grid, Agent, Competition){
        var vm = this;

        vm.models = {
            selected: null,
            lists: {"Available": [], "GridPosition": []}
        };

        vm.destroy = destroy;
        vm.getAgents = getAgents;
        vm.associate = associate;
        vm.disassociate = disassociate;
        vm.getCompetition = getCompetition;
        var username;
        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;
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
                $route.reload();
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
            Agent.getByGroup(vm.team).then(getByGroupSuccessFn, getByGroupErrorFn);
            Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);


        }

        function getByGroupSuccessFn(data){
            vm.models.lists.Available = [];
            for (var i = 0; i < data.data.length; ++i) {
                vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
            }

        }

        function getByGroupErrorFn(data){
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

        function associate(agent_name){
            console.log(vm.models.lists);

            var pos = vm.models.lists.GridPosition.length;
            Grid.associateAgent(agent_name, vm.identifier, pos).then(associateSuccessFn, associateErrorFn);

            function associateSuccessFn(){
                $.jGrowl("Agent has been associated successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getByGroup(vm.team).then(getByGroupSuccessFn, getByGroupErrorFn);

            }

            function associateErrorFn(data){
                console.error(data.data);
            }

        }

        function disassociate(pos){
            Grid.disassociateAgent(vm.identifier, pos).then(disassociateSuccessFn, disassociateErrorFn);
            console.log(vm.models.lists.GridPosition);
            function disassociateSuccessFn(){
                $.jGrowl("Agent has been disassociated successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                Agent.getByGroup(vm.team).then(getByGroupSuccessFn, getByGroupErrorFn);

                function getByGroupSuccessFn(data){
                    vm.models.lists.Available = [];
                    for (var i = 0; i < data.data.length; ++i) {
                        vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                    }
                    console.log(vm.models.lists.Available);
                    Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);


                }

                function getByGroupErrorFn(data){
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
                        gridAssociate(vm.models.lists.GridPosition[k].label, k+1);
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

        function gridAssociate(agent_name, pos){
            Grid.associateAgent(agent_name, vm.identifier, pos).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                Grid.getAgents(vm.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getByGroup(vm.team).then(getByGroupSuccessFn, getByGroupErrorFn);
            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }
        }

    }
})();