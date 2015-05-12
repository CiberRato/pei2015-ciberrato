(function(){
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('TeamController', TeamController);

    TeamController.$inject = ['$location', '$routeParams', '$timeout', 'Team', 'Authentication', 'Profile', 'Agent', '$scope'];

    function TeamController($location, $routeParams, $timeout, Team, Authentication, Profile, Agent, $scope){
        var vm = this;

        vm.addMember = addMember;
        vm.removeAdmin = removeAdmin;
        vm.addAdmin = addAdmin;
        vm.removeMember = removeMember;
        vm.destroy = destroy;
        var username;
        var teamName;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;
            teamName = $routeParams.name;

            Team.getMembers(teamName).then(getMembersSuccessFn, getMembersErrorFn);

            function getMembersSuccessFn(data){
                vm.members = data.data;
                for(var i = 0; i<vm.members.length; i++){
                    Team.getTeamInformation(teamName,vm.members[i].username).then(getTeamInformationSuccessFn, getTeamInformationErrorFn);
                }

                Profile.get(username).then(getUserSuccessFn, getUserErrorFn);


            }

            function getMembersErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }


        }

        function getUserSuccessFn(data){
            vm.member = data.data;
            Team.getTeamInformation(teamName, username).then(getTeamInformationUserSuccessFn, getTeamInformationUserErrorFn);

            function getTeamInformationUserSuccessFn(data){
                vm.memberInfo = data.data;
                vm.member.is_admin = vm.memberInfo.is_admin;
                $scope.loader.loading=true;


            }

            function getTeamInformationUserErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function getUserErrorFn(data){
            console.error(data.data);
            $location.path('/panel/');
        }

        function getTeamInformationSuccessFn(data){
            vm.team = data.data;
            for(var i = 0; i < vm.members.length; i++){
                if(vm.team.account.username === vm.members[i].username) {
                    vm.members[i].is_admin = vm.team.is_admin;
                }
            }







        }

        function getTeamInformationErrorFn(){
            $location.path('/panel/');
        }

        function addMember(){
            Team.addMember(vm.username, teamName).then(addMemberSuccessFn, addMemberErrorFn);
        }

        function addMemberSuccessFn(){
            $.jGrowl("Member has been added successfully to the Team.", {
                life: 2500,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
            });
            $timeout(function(){
                getMembers();
            });        }

        function addMemberErrorFn(data){
            var errors = "";
            if(typeof data.data.detail != "undefined"){
                errors +="Member " + data.data.detail;
            }
            else{
                if (typeof data.data.message == 'object'){
                    for (var value in data.data.message) {
                        errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                        for (var error in data.data.message[value]){
                            errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                        }
                    }
                }
                else{
                    errors+= data.data.message + '<br/>'
                }
            }
            $.jGrowl(errors, {
                life: 5000,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
            });
        }

        function removeAdmin(user_name, i){
            Team.manageAdmin(teamName, user_name).then(removeAdminSuccessFn, removeAdminErrorFn);

            function removeAdminSuccessFn(){
                $.jGrowl("Admin removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    getAdmin(i);
                });         }

            function removeAdminErrorFn(data){
                console.log(data.data);
                var errors = "";
                if(typeof data.data.detail != "undefined"){
                    errors += data.data.detail;
                }
                else{
                    if (typeof data.data.message == 'object'){
                        for (var value in data.data.message) {
                            errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                            for (var error in data.data.message[value]){
                                errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                            }
                        }
                    }
                    else{
                        errors+= data.data.message + '<br/>'
                    }
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });

            }
        }



        function addAdmin(user_name, i){
            Team.manageAdmin(teamName, user_name).then(addAdminSuccessFn, addAdminErrorFn);

            function addAdminSuccessFn(){
                $.jGrowl("Admin has been added successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    getAdmin(i);
                });         }

            function addAdminErrorFn(data){

                var errors = "";
                if(typeof data.data.detail != "undefined"){
                    errors += data.data.detail;
                }

                $.jGrowl(errors, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }

        }


        function removeMember(user_name){
            Team.removeMember(user_name, teamName).then(removeMemberSuccessFn, removeMemberErrorFn);
        }

        function removeMemberSuccessFn(){
            $.jGrowl("Member has been removed successfully of the Team.", {
                life: 2500,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
            });
            $timeout(function(){
                getMembers();
            });         }

        function removeMemberErrorFn(data) {
            console.error(data.data);
            $.jGrowl("Member can't be removed from Team.", {
                life: 2500,
                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
            });
        }

        function destroy(){
            Team.destroy(teamName).then(destroySuccessFn, destroyErrorFn);

            function destroySuccessFn(){
                $.jGrowl("Team has been deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.path("/panel/" + username + "/myTeams");
            }

            function destroyErrorFn(data){
                console.error(data.data);
                $.jGrowl("Team could not be deleted.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function getMembers(){
            Team.getMembers(teamName).then(getMembersSuccessFn, getMembersErrorFn);

            function getMembersSuccessFn(data){
                vm.members = data.data;
                for(var i = 0; i<vm.members.length; i++){
                    Team.getTeamInformation(teamName,vm.members[i].username).then(getTeamInformationSuccessFn, getTeamInformationErrorFn);
                }

            }

            function getMembersErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function getAdmin(i){
            Team.getTeamInformation(teamName,vm.members[i].username).then(getTeamInformationSuccessFn, getTeamInformationErrorFn);

            function getTeamInformationSuccessFn(data){
                vm.team = data.data;
                vm.members[i].is_admin = vm.team.is_admin;

            }

            function getTeamInformationErrorFn(){
                $location.path('/panel/');
            }
        }



    }
})();
