(function(){
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('TeamController', TeamController);

    TeamController.$inject = ['$location', '$routeParams','Team', 'Authentication', 'Profile', 'Agent'];

    function TeamController($location, $routeParams, Team, Authentication, Profile, Agent){
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
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;
            teamName = $routeParams.name;

            Team.getMembers(teamName).then(getMembersSuccessFn, getMembersErrorFn);
            Team.getTeamInformation(teamName, username).then(getTeamInformationSuccessFn, getTeamInformationErrorFn);
            Profile.get(username).then(getUserSuccessFn, getUserErrorFn);
            Agent.getByGroup(teamName).then(getByGroupSuccessFn, getByGroupErrorFn);

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

            function getUserSuccessFn(data){
                vm.member = data.data;
                Team.getTeamInformation(teamName, username).then(getTeamInformationUserSuccessFn, getTeamInformationUserErrorFn);
            }

            function getUserErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getTeamInformationUserSuccessFn(data){
                vm.memberInfo = data.data;
                vm.member.is_admin = vm.memberInfo.is_admin;

            }

            function getTeamInformationUserErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getByGroupSuccessFn(data){
                vm.agents = data.data;
            }

            function getByGroupErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
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
                theme: 'success'
            });
            $location.path('/panel/' + teamName + '/editTeam/');
        }

        function addMemberErrorFn(data){
            console.error(data.data);
            $.jGrowl("Member could not be added to the Team.", {
                life: 2500,
                theme: 'btn-danger'
            });
        }

        function removeAdmin(user_name){
            Team.manageAdmin(teamName, user_name).then(removeAdminSuccessFn, removeAdminErrorFn);
        }

        function removeAdminSuccessFn(){
            $.jGrowl("Admin has been removed successfully.", {
                life: 2500,
                theme: 'success'
            });
            $location.path('/panel/' + teamName + '/editTeam/');
        }

        function removeAdminErrorFn(data){
            console.error(data.data);
            $.jGrowl("Admin could not be removed.", {
                life: 2500,
                theme: 'btn-danger'
            });
        }

        function addAdmin(user_name){
            Team.manageAdmin(teamName, user_name).then(addAdminSuccessFn, addAdminErrorFn);
        }

        function addAdminSuccessFn(){
            $.jGrowl("Admin has been added successfully.", {
                life: 2500,
                theme: 'success'
            });
            $location.path('/panel/' + teamName + '/editTeam/');
        }

        function addAdminErrorFn(data){
            console.error(data.data);
            $.jGrowl("Admin could not be added.", {
                life: 2500,
                theme: 'btn-danger'
            });
        }

        function removeMember(user_name){
            Team.removeMember(user_name, teamName).then(removeMemberSuccessFn, removeMemberErrorFn);
        }

        function removeMemberSuccessFn(){
            $.jGrowl("Member has been removed successfully of the Team.", {
                life: 2500,
                theme: 'success'
            });
            $location.path('/panel/' + teamName + '/editTeam/');
        }

        function removeMemberErrorFn(data) {
            console.error(data.data);
            $.jGrowl("Member could not be removed of the Team.", {
                life: 2500,
                theme: 'btn-danger'
            });
        }

        function destroy(){
            Team.destroy(teamName).then(destroySuccessFn, destroyErrorFn);

            function destroySuccessFn(){
                $.jGrowl("Team has been deleted.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path("/panel/" + username + "/myTeams");
            }

            function destroyErrorFn(data){
                console.error(data.data);
                $.jGrowl("Team could not be deleted.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }



    }
})();
