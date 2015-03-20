(function () {
    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('MyAgentsController', MyAgentsController);

    MyAgentsController.$inject = ['$location', 'Authentication', 'Agent', 'Team'];

    function MyAgentsController($location, Authentication, Agent) {
        var vm = this;

        activate();

        function activate() {
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            vm.username = authenticatedAccount.username;

            Agent.getByUser(vm.username).then(getByUserSuccessFn, getByUserErrorFn);

            function getByUserSuccessFn(data) {
                vm.agents = data.data;
            }

            function getByUserErrorFn(data) {
                console.error(data.data);
                $location.path("/panel/")
            }

        }
    }
})();