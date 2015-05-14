(function(){

	'use strict';

	angular
		.module('ciberonline.teams.controllers')
		.controller('AllTeamsController', AllTeamsController);

	AllTeamsController.$inject = ['$location', 'Team', '$scope'];

	function AllTeamsController($location, Team, $scope){
		var vm = this;
        vm.change = change;
		activate();

		function activate(){
            $scope.loader = {
                loading: false
            };
			Team.getAll().then(getAllSuccessFn, getAllErrorFn);

        	function getAllSuccessFn(data){
        		vm.team = data.data.results;

                for(var i=0; i<vm.team.length; i++){
                    console.log(vm.team[i]);
                    getNumberOfMembers(vm.team[i].name, i);
                }
                $scope.loader = {
                    loading: true
                };

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