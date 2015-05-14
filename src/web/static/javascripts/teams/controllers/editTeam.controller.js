(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('EditTeamController', EditTeamController);

    EditTeamController.$inject = ['$location', '$routeParams', 'Authentication', 'Team', '$scope'];

    function EditTeamController($location, $routeParams, Authentication, Team, $scope){
        var vm = this;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();
        var username = authenticatedAccount.username;
        var teamName;
        vm.update = update;
        vm.destroy = destroy;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            teamName = $routeParams.name;

            Team.getTeam(teamName).then(getTeamSuccessFn, getTeamErrorFn);

            function getTeamSuccessFn(data){
                vm.team = data.data;
                $scope.loader = {
                    loading: true
                };
            }

            function getTeamErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function update(){
            Team.update(vm.team, teamName).then(updateTeamSuccessFn, updateTeamErrorFn);

            function updateTeamSuccessFn(){
                $.jGrowl("Team has been updated.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.path("/panel/" + username + "/myTeams");
            }

            function updateTeamErrorFn(data){
                var errors = "";
                for (var value in data.data.message) {
                    errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                    for (var error in data.data.message[value]){
                        errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                    }
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function destroy(){
            Team.destroy(teamName).then(destroyTeamSuccessFn, destroyTeamErrorFn);

            function destroyTeamSuccessFn(){
                $.jGrowl("Team has been deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.path("/panel/" + username + "/myTeams");
            }

            function destroyTeamErrorFn(data){
                $.jGrowl("Team can't be deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                console.error(data.data);
            }

        }
    }
})();

