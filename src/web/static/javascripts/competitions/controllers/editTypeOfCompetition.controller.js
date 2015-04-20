(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('EditTypeOfCompetitionController', EditTypeOfCompetitionController);

    EditTypeOfCompetitionController.$inject = ['$location', '$routeParams', 'Competition'];

    function EditTypeOfCompetitionController($location, $routeParams, Competition){
        var vm=this;
        var typeName;
        vm.update = update;

        activate();

        function activate(){
            typeName = $routeParams.name;

            Competition.getType(typeName).then(getTypeSuccessFn, getTypeErrorFn);

            function getTypeSuccessFn(data){
                vm.type = data.data;
                console.log(vm.type);
            }

            function getTypeErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function update(){
            Competition.updateType(vm.type, typeName).then(updateTeamSuccessFn, updateTeamErrorFn);

            function updateTeamSuccessFn(){
                $.jGrowl("Team has been updated.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path("/admin/allTypesOfCompetition");
            }

            function updateTeamErrorFn(data){
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