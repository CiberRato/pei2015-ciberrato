(function () {
    'use strict';

    angular
        .module('ciberonline.profile.controllers')
        .controller('ProfileController', ProfileController);

    ProfileController.$inject = ['$location', '$routeParams', 'Authentication', 'Profile'];

    function ProfileController($location, $routeParams, Authentication, Profile){
        var vm = this;

        vm.update = update;

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

            Profile.get(username).then(profileSuccessFn, profileErrorFn);

            function profileSuccessFn(data, status, headers, config){
                vm.profile = data.data;
            }

            function profileErrorFn(data, status, headers, config){
                $location.url('/');
            }
        }

        function update(){
            Profile.update(vm.profile).then(profileSuccessFn, profileErrorFn);

            function profileSuccessFn(data, status, headers, config){
                window.location.assign("/panel/")
            }

            function profileErrorFn(data, status, headers, config){

            }
        }
    }
})();
