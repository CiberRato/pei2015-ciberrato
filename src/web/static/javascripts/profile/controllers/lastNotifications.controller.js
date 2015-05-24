(function () {
    'use strict';

    angular
        .module('ciberonline.profile.controllers')
        .controller('LastNotificationsController', LastNotificationsController);

    LastNotificationsController.$inject = ['$location', 'Profile', '$scope', 'Users', 'Notification'];

    function LastNotificationsController($location, Profile, $scope, Users, Notification){
        var vm = this;

        activate();

        function activate() {
            $scope.loader = {
                loading: false
            };

            Notification.activateNotifications();

            vm.user=Users.getMe().then(success, error);

            function success(data){
                vm.user = data.data;
                Profile.getBroadcastNotifications().then(getBroadcastNotificationsSuccessFn, getBroadcastNotificationsErrorFn);
                console.log(vm.user);

            }
            function error(data){
                console.error(data.data);
            }


            function getBroadcastNotificationsSuccessFn(data) {
                vm.broadcast = data.data;
                console.log(vm.broadcast);
                if(vm.broadcast.length > 0) {
                    for (var i = 0; i < vm.broadcast.length; i++) {
                        vm.broadcast[i].content = convert(vm.broadcast[i].message);
                        if (vm.broadcast[i].content.status == 100) {
                            vm.status = "alert-info"
                        } else if (vm.broadcast[i].content.status == 200) {
                            vm.status = "alert-success"
                        } else if (vm.broadcast[i].content.status == 400) {
                            vm.status = "alert-error"
                        }
                    }
                }
                Profile.getAdminNotifications().then(getAdminNotificationsSuccessFn, getAdminNotificationsErrorFn);

                function getAdminNotificationsSuccessFn(data) {
                    vm.admin = data.data;
                    console.log(vm.admin);
                    if(vm.admin.length > 0) {
                        for (var i = 0; i < vm.admin.length; i++) {
                            vm.admin[i].content = convert(vm.admin[i].message);
                            if (vm.admin[i].content.status == 100) {
                                vm.status = "alert-info"
                            } else if (vm.admin[i].content.status == 200) {
                                vm.status = "alert-success"
                            } else if (vm.admin[i].content.status == 400) {
                                vm.status = "alert-error"
                            }
                        }
                    }

                    Profile.getUserNotifications().then(getUserNotificationsSuccessFn, getUserNotificationsErrorFn);

                    function getUserNotificationsSuccessFn(data) {
                        vm.user = data.data;
                        if(vm.user.length > 0) {
                            for (var i = 0; i < vm.user.length; i++) {
                                vm.user[i].content = convert(vm.user[i].message);
                                if (vm.user[i].content.status == 100) {
                                    vm.status = "alert-info"
                                } else if (vm.user[i].content.status == 200) {
                                    vm.status = "alert-success"
                                } else if (vm.user[i].content.status == 400) {
                                    vm.status = "alert-error"
                                }
                            }
                        }
                        console.log(vm.user);
                        Profile.getTeamNotifications().then(getTeamNotificationsSuccessFn, getTeamNotificationsErrorFn);

                        function getTeamNotificationsSuccessFn(data) {
                            vm.team = data.data;
                            console.log(vm.team);
                            if(vm.team.length > 0) {
                                for (var i = 0; i < vm.team.length; i++) {
                                    for (var j = 0; j < vm.team[i].notifications.length; j++) {
                                        vm.team[i].notifications[j].content = convert(vm.team[i].notifications[j].message);
                                        if (vm.team[i].notifications[j].content.status == 100) {
                                            vm.status = "alert-info"
                                        } else if (vm.team[i].notifications[j].content.status == 200) {
                                            vm.status = "alert-success"
                                        } else if (vm.team[i].notifications[j].content.status == 400) {
                                            vm.status = "alert-error"
                                        }
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
