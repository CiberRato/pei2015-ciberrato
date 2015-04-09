(function () {
    'use strict';

    angular
        .module("ciberonline.teams.services")
        .factory("Team", Team);

    Team.$inject = ['$http'];

    function Team($http){
        var Team = {
            create: create,
            getAll: getAll,
            getByUser: getByUser,
            getTeamInformation: getTeamInformation,
            getMembers: getMembers,
            addMember: addMember,
            manageAdmin: manageAdmin,
            removeMember: removeMember,
            update: update,
            getTeam: getTeam,
            destroy: destroy,
            getUserAdmin: getUserAdmin,
            change: change
        };

        return Team;

        function create(name, max_members){
            return $http.post('api/v1/groups/crud/', {
                name: name,
                max_members: max_members
            });

        }

        function getAll(){
            return $http.get('api/v1/groups/crud/');
        }

        function getByUser(username){
            return $http.get('api/v1/groups/user/' + username + '/');
        }

        function getTeamInformation(teamName, username){
            return $http.get('api/v1/groups/member/' + teamName +'/?username=' + username);
        }

        function getTeam(teamName){
            return $http.get('api/v1/groups/crud/' + teamName + '/');
        }

        function getMembers(teamName){
            return $http.get('api/v1/groups/members/' + teamName + '/');
        }

        function addMember(user_name, group_name){
            return $http.post('api/v1/groups/member/', {
                group_name: group_name,
                user_name: user_name
            });

        }

        function manageAdmin(group_name, user_name){
            return $http.put('api/v1/groups/admin/'+ group_name + '/?username=' + user_name);
        }

        function removeMember(user_name, group_name){
            return $http.delete('api/v1/groups/member/' + group_name + '/?username=' + user_name);
        }

        function update(team, teamName){
            return $http.put('api/v1/groups/crud/' + teamName + "/", {
                name: team.name,
                max_members: team.max_members

            });
        }

        function destroy(teamName){
            return $http.delete('api/v1/groups/crud/' + teamName + '/');
        }

        function getUserAdmin(username){
            return $http.get('api/v1/groups/user_admin/' + username +'/');
        }

        function change(url){
            return $http.get(url);
        }

    }


})();

