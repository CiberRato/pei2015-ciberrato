(function(){

	'use strict';

	angular
		.module('ciberonline.teams.controllers')
		.controller('AllTeamsController', AllTeamsController);

	AllTeamsController.$inject = ['$location', 'Team'];

	function AllTeamsController($location, Team){
		var vm = this;

		activate();

		function activate(){
			console.log("all")
			Team.getAll().then(getAllSuccessFn, getAllErrorFn);
			

        	function getAllSuccessFn(data, status, headers, config){
        		vm.team = data.data;
        	}

       		function getAllErrorFn(data, status, headers, config){
       			$location.url('/');
   			}
      		
		}
		

	}

})();