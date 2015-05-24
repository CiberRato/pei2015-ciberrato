(function(){

    'use strict';

    angular
        .module('ciberonline.users.controllers')
        .controller('ChangePermissionsController', ChangePermissionsController);

    ChangePermissionsController.$inject = ['$location', 'Users', '$scope', 'Authentication', 'Notification'];

    function ChangePermissionsController($location, Users, $scope, Authentication, Notification){
        var vm = this;
        vm.change = change;
        vm.removeStaff = removeStaff;
        vm.addStaff = addStaff;
        vm.removeSuperUser = removeSuperUser;
        vm.addSuperUser = addSuperUser;
        vm.login = login;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Notification.activateNotifications();

            Users.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.users = data.data;
                Users.getMe().then(getSuccessFn, getErrorFn);

                function getSuccessFn(data){
                    vm.user = data.data;
                    console.log(vm.user);
                    $scope.loader = {
                        loading: true
                    };
                }
                function getErrorFn(data){
                    console.error(data.data);
                    $location.url('/panel/');
                }
                console.log(vm.users);
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

        }

        function change(url){
            Users.change(url).then(changeSuccessFn, changeErrorFn);

            function changeSuccessFn(data){
                vm.users = data.data;
            }

            function changeErrorFn(data){
                console.error(data.data);
            }
        }

        function removeStaff(username, i){
            Users.toggleStaff(username).then(toggleStaffSuccessFn, toggleStaffErrorFn);

            function toggleStaffSuccessFn(){
                $.jGrowl("User "+ username + " has been removed from Staff successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                /*$timeout(function(){
                    getAdmin(i);
                });*/
            }

            function toggleStaffErrorFn(data){
                console.error(data.data);
            }

        }

        function addStaff(username, i){
            Users.toggleStaff(username).then(toggleStaffSuccessFn, toggleStaffErrorFn);

            function toggleStaffSuccessFn(){
                $.jGrowl("User "+ username + " has been added to Staff successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                /*$timeout(function(){
                 getAdmin(i);
                 });*/
            }

            function toggleStaffErrorFn(data){
                console.error(data.data);
            }

        }

        function removeSuperUser(username, i){
            Users.toggleSuperUser(username).then(toggleStaffSuccessFn, toggleStaffErrorFn);

            function toggleStaffSuccessFn(){
                $.jGrowl("User "+ username + " has been removed from SuperUser successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                /*$timeout(function(){
                 getAdmin(i);
                 });*/
            }

            function toggleStaffErrorFn(data){
                console.error(data.data);
            }

        }

        function addSuperUser(username, i){
            Users.toggleSuperUser(username).then(toggleStaffSuccessFn, toggleStaffErrorFn);

            function toggleStaffSuccessFn(){
                $.jGrowl("User "+ username + " has been added to SuperUser successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                /*$timeout(function(){
                 getAdmin(i);
                 });*/
            }

            function toggleStaffErrorFn(data){
                console.error(data.data);
            }

        }

        function login(username){
            Users.login(username).then(loginSuccessFn, loginErrorFn);

            function loginSuccessFn(data){
                $.jGrowl("User "+ username + " has been logged by you successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                Authentication.setAuthenticatedAccount(data.data);
                window.location.assign("/panel/")
            }

            function loginErrorFn(data){
                console.error(data.data);
            }
        }

    }

})();