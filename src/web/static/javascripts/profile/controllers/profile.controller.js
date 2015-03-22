(function () {
    'use strict';

    angular
        .module('ciberonline.profile.controllers')
        .controller('ProfileController', ProfileController);

    ProfileController.$inject = ['$location', '$routeParams', 'Authentication', 'Profile'];

    function ProfileController($location, $routeParams, Authentication, Profile){
        var vm = this;

        vm.update = update;
        vm.updatePassword = updatePassword;
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

            function profileSuccessFn(data){
                vm.profile = data.data;
            }

            function profileErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function update(){
            Profile.update(vm.profile).then(profileUpdateSuccessFn, profileUpdateErrorFn);

            function profileUpdateSuccessFn(){
                $.jGrowl("Profile has been updated.", {
                    life: 2500,
                    theme: 'success'
                });
                window.location.assign("/panel/");
            }

            function profileUpdateErrorFn(data){
                $.jGrowl("Profile could not be updated.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }
        }

        function updatePassword(){
            Profile.updatePassword(vm.profile.username,vm.profile.password, vm.profile.confirm_password).then(profilePassSuccessFn, profilePassErrorFn);

            function profilePassSuccessFn(){
                $.jGrowl("Password has been updated.", {
                    life: 2500,
                    theme: 'success'
                });
                window.location.assign("/");
            }

            function profilePassErrorFn(data){
                $.jGrowl("Password could not be updated.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }
        }

        function destroy(){
            Profile.destroy(vm.profile.username).then(destroyProfileSuccessFn, destroyProfileErrorFn);

            function destroyProfileSuccessFn(){
                $.jGrowl("Profile has been deleted.", {
                    life: 2500,
                    theme: 'success'
                });
                window.location.assign("/");
            }

            function destroyProfileErrorFn(data){
                $.jGrowl("Profile could not be deleted.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }

        }
    }
})();
