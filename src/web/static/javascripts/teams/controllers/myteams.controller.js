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
                vm.team.count = vm.team.length;
                vm.team.username = username;
            }

            function getByUserErrorFn(data, status, headers, config){
                console.error(data.data);
            	$location.path('/panel/');
            }
		}
	}
})();