(function(){

    'use strict';

    angular
        .module('ciberonline.users.controllers')
        .controller('ChangePermissionsController', ChangePermissionsController);

    ChangePermissionsController.$inject = ['$location', 'Users', '$route'];

    function ChangePermissionsController($location, Users){
        var vm = this;
        vm.change = change;
        activate();

        function activate(){
            Users.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.users = data.data;
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

    }

})();