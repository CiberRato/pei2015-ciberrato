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
			Team.getAll().then(getAllSuccessFn, getAllErrorFn);

        	function getAllSuccessFn(data, status, headers, config){
        		vm.team = data.data;
                for(var i=0; i<vm.team.length; i++){
                    console.log(vm.team[i].name);
                    getNumberOfMembers(vm.team[i].name, i);
                }

        	}

       		function getAllErrorFn(data, status, headers, config){
       			$location.url('/');
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