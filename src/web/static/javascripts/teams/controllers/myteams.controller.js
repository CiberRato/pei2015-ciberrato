(function(){
	'use strict';

	angular
		.module('ciberonline.teams.controllers')
		.controller('MyTeamsController', MyTeamsController);

	MyTeamsController.$inject = ['$location', '$routeParams','$timeout','Team', 'Authentication', 'Agent'];

	function MyTeamsController($location, $routeParams, $timeout, Team, Authentication, Agent){
		var vm = this;
        vm.destroy = destroy;
        var username = $routeParams.username;

		activate();

		function activate(){
			var authenticatedAccount = Authentication.getAuthenticatedAccount();

            if(!authenticatedAccount){
                $location.url('/');
            }else{
                if(authenticatedAccount.username !== username){
                    $location.url('/');
                }
            }

            Team.getByUser(username).then(getByUserSuccessFn, getByUserErrorFn);


		}
        function destroy(teamName){
            Team.destroy(teamName).then(destroyTeamSuccessFn, destroyTeamErrorFn);

            function destroyTeamSuccessFn(){
                $.jGrowl("Team has been deleted.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    Team.getByUser(username).then(getByUserSuccessFn, getByUserErrorFn);

                });
            }

            function destroyTeamErrorFn(data){
                $.jGrowl("Team can't be deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                console.error(data.data);
            }

        }

        function getByUserSuccessFn(data){
            vm.team = data.data;
            vm.team.username = username;
            for(var i=0; i<vm.team.length; i++){
                getNumberOfMembers(vm.team[i].name, i);
                getNumberOfAgents(vm.team[i].name, i);
            }
        }

        function getByUserErrorFn(data){
            console.error(data.data);
            $location.path('/panel/');
        }

        function getNumberOfMembers(teamName, i){
            Team.getMembers(teamName).then(getNumberOfMembersSuccessFn, getNumberOfMembersErrorFn);

            function getNumberOfMembersSuccessFn(data) {
                vm.members = data.data;
                vm.team[i].allmembers = vm.members.length;
            }

            function getNumberOfMembersErrorFn(data){
                console.error(data.data);
            }

        }

        function getNumberOfAgents(teamName, i){
            Agent.getByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

            function getByTeamSuccessFn(data) {
                vm.agents = data.data;
                vm.team[i].allAgents = vm.agents.length;
            }

            function getByTeamErrorFn(data){
                console.error(data.data);
            }
        }
	}
})();