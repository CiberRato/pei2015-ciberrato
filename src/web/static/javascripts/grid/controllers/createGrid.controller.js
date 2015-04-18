(function () {
    'use strict';

    angular
        .module('ciberonline.grid.controllers')
        .controller('CreateGridPositionController', CreateGridPositionController);

    CreateGridPositionController.$inject = ['$location', '$route', 'Authentication', 'Grid', 'Competition', 'Team'];

    function CreateGridPositionController($location, $route, Authentication, Grid, Competition, Team){
        var vm = this;

        vm.change = change;
        vm.create = create;
        var username;
        vm.competitions = [];
        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;
            Team.getByUser(username).then(getSuccessFn, getErrorFn);

            function getSuccessFn(data){
                vm.teams = data.data;
                console.log(vm.teams);
            }

            function getErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

        }

        function change(teamName){
            Competition.getValidByTeam(teamName).then(getValidSuccessFn, getValidErrorFn);

            function getValidSuccessFn(data){
                vm.competitions = data.data;
                console.log(vm.competitions);
            }

            function getValidErrorFn(data){
                vm.competitions = [];
                console.error(data.data);
            }
        }

        function create(){
            var teamName;
            var competitionName;

            if(vm.teams.length > 0){
                teamName = document.getElementById("select1").value;
            }else{
                teamName = undefined;
            }
            if(vm.competitions.length > 0){
                competitionName = document.getElementById("select").value;
            }else{
                competitionName = undefined;
            }

            Grid.create(teamName, competitionName).then(createSuccessFn, createErrorFn);

            function createSuccessFn(data){
                console.log(data.data);
                $.jGrowl("Grid Position has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/panel/myGridPositions/');
            }

            function createErrorFn(data){
                console.error(data.data);
                $.jGrowl("Grid Position could not be created.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }
        }

    }
})();
