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
            console.log("myteams")
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
            }

            function getByUserErrorFn(data, status, headers, config){
            	$location.path('/panel/');
            }
		}
	}
})();