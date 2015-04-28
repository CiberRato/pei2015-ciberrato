(function(){

    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('CreateRoundController', CreateRoundController);

    CreateRoundController.$inject = ['$location', '$route', '$routeParams', 'Round'];

    function CreateRoundController($location, $route, $routeParams, Round){
        var vm = this;

        vm.create = create;
        vm.competitionName = $routeParams.name;
        activate();

        function activate() {

        }

        function create(){
            Round.create(vm.roundName, vm.competitionName).then(createSuccessFn, createErrorFn);

            function createSuccessFn(){
                $.jGrowl("Round has been created successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.path('/admin/' + vm.competitionName + "/");
            }

            function createErrorFn(data){
                console.log(data.data);
                var errors = "";
                if(typeof data.data.detail != "undefined"){
                    errors += data.data.detail;
                }
                else{
                    if (typeof data.data.message == 'object'){
                        for (var value in data.data.message) {
                            errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                            for (var error in data.data.message[value]){
                                errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                            }
                        }
                    }
                    else{
                        errors+= data.data.message + '<br/>'
                    }
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                $route.reload();
            }
        }

    }

})();


