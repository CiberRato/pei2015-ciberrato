(function () {
    'use strict';

    angular
        .module('ciberonline.profile.controllers')
        .controller('LastNotificationsController', LastNotificationsController);

    LastNotificationsController.$inject = ['$location', 'Profile', '$scope'];

    function LastNotificationsController($location, Profile, $scope){
        var vm = this;

        activate();

        function activate() {
            $scope.loader = {
                loading: false
            };

            Profile.getBroadcastNotifications().then(getBroadcastNotificationsSuccessFn, getBroadcastNotificationsErrorFn);

            function getBroadcastNotificationsSuccessFn(data) {
                vm.broadcast = data.data;
                console.log(vm.broadcast);
                Profile.getAdminNotifications().then(getAdminNotificationsSuccessFn, getAdminNotificationsErrorFn);

                function getAdminNotificationsSuccessFn(data) {
                    vm.admin = data.data;
                    console.log(vm.admin);

                    Profile.getUserNotifications().then(getUserNotificationsSuccessFn, getUserNotificationsErrorFn);

                    function getUserNotificationsSuccessFn(data) {
                        vm.user = data.data;
                        console.log(vm.user);
                        Profile.getTeamNotifications().then(getTeamNotificationsSuccessFn, getTeamNotificationsErrorFn);

                        function getTeamNotificationsSuccessFn(data) {
                            vm.team = data.data;
                            console.log(vm.team);
                            for (var i = 0; i < vm.team.length; i++) {
                                for (var j = 0; j < vm.team[i].notifications.length; j++) {
                                    vm.team[i].notifications[j].content = convert(vm.team[i].notifications[j].message);
                                    if(vm.team[i].notifications[j].content.status == 100){
                                        vm.ola = "alert-error"
                                    }
                                }
                            }
                            console.log();

                            console.log(vm.team);
                            $scope.loader = {
                                loading: true
                            };
                        }

                        function getTeamNotificationsErrorFn(data) {
                            console.error(data.data);
                        }
                    }

                    function getUserNotificationsErrorFn(data) {
                        console.error(data.data);
                    }

                }

                function getAdminNotificationsErrorFn(data) {
                    console.error(data.data);
                }


            }

            function getBroadcastNotificationsErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function convert(str){
            var res = str.replace(/u'/g, "'");
            res = res.replace(/'/g, '"');
            return JSON.parse(res);

        }


    }
})();
