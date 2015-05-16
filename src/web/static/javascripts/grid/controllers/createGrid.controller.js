(function () {
    'use strict';

    angular
        .module('ciberonline.grid.controllers')
        .controller('CreateGridPositionController', CreateGridPositionController);

    CreateGridPositionController.$inject = ['$location', '$scope', 'Authentication', 'Grid', 'Competition', 'Team'];

    function CreateGridPositionController($location, $scope, Authentication, Grid, Competition, Team){
        var vm = this;

        vm.change = change;
        vm.create = create;
        var username;
        vm.competitions = [];
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;
            Team.getByUser(username).then(getSuccessFn, getErrorFn);

            function getSuccessFn(data){
                vm.teams = data.data;
                console.log(vm.teams);
                $scope.loader = {
                    loading: true
                };
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
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.path('/panel/myGridPositions/');
            }

            function createErrorFn(data){
                var errors = "";

                if (typeof data.data.message === 'object'){
                    for (var value in data.data.message) {
                        errors += "&bull;" + value.replace("_", " ") + ":<br/>"
                        for (var error in data.data.message[value]){
                            errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                        }
                    }
                }else{
                    errors = data.data.message;
                }
                if(typeof data.data.detail !== 'undefined'){
                    errors += " &nbsp; "+ data.data.detail + '<br/>';
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });

            }
        }

    }
})();
