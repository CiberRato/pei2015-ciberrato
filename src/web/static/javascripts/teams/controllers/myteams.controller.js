(function(){
	'use strict';

	angular
		.module('ciberonline.teams.controllers')
		.controller('MyTeamsController', MyTeamsController);

	MyTeamsController.$inject = ['$location', '$routeParams','Team', 'Authentication'];

	function MyTeamsController($location, $routeParams, Team, Authentication){
		var vm = this;

		activate();

		function activate(){
			var authenticatedAccount = Authentication.getAuthenticatedAccount();
            var username = $routeParams.username;

            if(!authenticatedAccount){
                $location.url('/');
            }else{
                if(authenticatedAccount.username !== username){
                    $location.url('/');
                }
            }

            Team.getByUser(username).then(getByUserSuccessFn, getByUserErrorFn);

            function getByUserSuccessFn(data, status, headers, config){
            	vm.team = data.data;
                vm.team.username = username;
                for(var i=0; i<vm.team.length; i++){
                    getNumberOfMembers(vm.team[i].name, i);
                }
            }

            function getByUserErrorFn(data, status, headers, config){
                console.error(data.data);
            	$location.path('/panel/');
            }

            function getNumberOfMembers(teamName, i){
                Team.getMembers(teamName).then(getNumberOfMembersSuccessFn, getNumberOfMembersErrorFn);

                function getNumberOfMembersSuccessFn(data, status, headers, config) {
                    vm.members = data.data;
                    vm.team[i].allmembers = vm.members.length;
                }

                function getNumberOfMembersErrorFn(data, status, headers, config){
                    console.error(data.data);
                }

            }
		}
	}
})();