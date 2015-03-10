(function(){

    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('MemberProfile', MemberProfile);

    MemberProfile.$inject = ['$location', '$routeParams', 'Team', 'Profile'];

    function MemberProfile($location,$routeParams, Team, Profile){
        var vm = this;
        var username = $routeParams.username;
        activate();

        function activate(){
            Team.getByUser(username).then(getByUserSuccessFn, getByUserErrorFn);
            Profile.get(username).then(getProfileSuccessFn, getProfileErrorFn);

            function getByUserSuccessFn(data, status, headers, config){
                vm.teams = data.data;
            }

            function getByUserErrorFn(data, status, headers, config){
                $location.url('/');
            }

            function getProfileSuccessFn(data, status, headers, config) {
                vm.accountInfo = data.data;
                vm.gravatar = get_gravatar(vm.accountInfo.email, 60);
            }

            function getProfileErrorFn(data, status, headers, config){
                console.error(data.data);
            }

        }


    }

})();
