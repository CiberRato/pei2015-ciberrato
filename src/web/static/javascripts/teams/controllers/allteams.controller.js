(function(){

	'use strict';

	angular
		.module('ciberonline.teams.controllers')
		.controller('AllTeamsController', AllTeamsController);

	AllTeamsController.$inject = ['$location', 'Team', '$route'];

	function AllTeamsController($location, Team, $route){
		var vm = this;
        vm.change = change;
		activate();

		function activate(){
			Team.getAll().then(getAllSuccessFn, getAllErrorFn);

        	function getAllSuccessFn(data){
        		vm.team = data.data;
                for(var i=0; i<vm.team.length; i++){
                    getNumberOfMembers(vm.team[i].name, i);
                }

                console.log(vm.team);

        	}

       		function getAllErrorFn(data){
                console.error(data.data);
       			$location.url('/panel/');
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

		}

        function change(url){
            Team.change(url).then(changeSuccessFn, changeErrorFn);

            function changeSuccessFn(data){
                vm.team = data.data;
            }

            function changeErrorFn(data){
                console.error(data.data);
            }
        }
		

	}

})();