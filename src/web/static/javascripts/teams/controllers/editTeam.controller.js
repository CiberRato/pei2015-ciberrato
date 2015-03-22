(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('EditTeamController', EditTeamController);

    EditTeamController.$inject = ['$location', '$routeParams', 'Authentication', 'Team'];

    function EditTeamController($location, $routeParams, Authentication, Team){
        var vm = this;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();
        var username = authenticatedAccount.username;
        var teamName;
        vm.update = update;
        vm.destroy = destroy;

        activate();

        function activate(){
            teamName = $routeParams.name;

            Team.getTeam(teamName).then(getTeamSuccessFn, getTeamErrorFn);

            function getTeamSuccessFn(data){
                vm.team = data.data;
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
                    theme: 'success'
                });
                $location.path("/panel/" + username + "/myTeams");
            }

            function updateTeamErrorFn(data){
                $.jGrowl("Team could not be updated.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }
        }

        function destroy(){
            Team.destroy(teamName).then(destroyTeamSuccessFn, destroyTeamErrorFn);

            function destroyTeamSuccessFn(){
                $.jGrowl("Team has been deleted.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path("/panel/" + username + "/myTeams");
            }

            function destroyTeamErrorFn(data){
                $.jGrowl("Team could not be deleted.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }

        }
    }
})();

