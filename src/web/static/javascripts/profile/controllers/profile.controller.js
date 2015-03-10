(function () {
    'use strict';

    angular
        .module('ciberonline.profile.controllers')
        .controller('ProfileController', ProfileController);

    ProfileController.$inject = ['$location', '$routeParams', 'Authentication', 'Profile'];

    function ProfileController($location, $routeParams, Authentication, Profile){
        var vm = this;

        vm.update = update;
        vm.destroy = destroy;

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
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function update(){
            Profile.update(vm.profile).then(profileSuccessFn, profileErrorFn);

            function profileSuccessFn(data, status, headers, config){
                $.jGrowl("Profile has been updated.", {
                    life: 2500,
                    theme: 'success'
                });
                window.location.assign("/panel/");
            }

            function profileErrorFn(data, status, headers, config){
                $.jGrowl("Profile could not be updated.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }
        }

        function destroy(){
            Profile.destroy(vm.profile.username).then(destroyProfileSuccessFn, destroyProfileErrorFn);

            function destroyProfileSuccessFn(data, status, headers, config){
                $.jGrowl("Profile has been deleted.", {
                    life: 2500,
                    theme: 'success'
                });
                window.location.assign("/");
            }

            function destroyProfileErrorFn(data, status, headers, config){
                $.jGrowl("Profile could not be deleted.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }

        }
    }
})();
