(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('CreateTypeOfCompetitionController', CreateTypeOfCompetitionController);

    CreateTypeOfCompetitionController.$inject = ['$location', 'Authentication', 'Competition', 'Round'];

    function CreateTypeOfCompetitionController($location, Authentication, Competition){
        var vm = this;

        vm.create = create;

        activate();

        function activate(){

        }

        function create(){
            Competition.createTypeOfCompetition(vm.typeOfCompetitionName, vm.teamsForTrial, vm.agentsByGrid).then(createSuccessFn, createErrorFn);

            function createSuccessFn(){
                $.jGrowl("Type Of Competition has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/allTypesOfCompetition/');

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
                    theme: 'btn-danger'
                });
            }

        }

    }
})();

