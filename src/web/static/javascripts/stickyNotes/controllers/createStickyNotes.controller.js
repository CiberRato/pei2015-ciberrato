(function(){

    'use strict';

    angular
        .module('ciberonline.stickyNotes.controllers')
        .controller('CreateStickyNotesController', CreateStickyNotesController);

    CreateStickyNotesController.$inject = ['StickyNotes', '$location'];

    function CreateStickyNotesController(StickyNotes, $location){
        var vm = this;

        vm.create = create;
        activate();

        function activate(){

        }

        function create(){
            console.log(vm.time);
            console.log(vm.text);

            StickyNotes.create(vm.text, vm.time).then(createSuccessFn, createErrorFn);

            function createSuccessFn(){
                $.jGrowl("Sticky Note has been created successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.path('/admin/stickyNotes/');
            }

            function createErrorFn(data){
                console.error(data.data);
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
                if(typeof data.data.detail !== 'undefined'){
                    errors += " &nbsp; "+ data.data.detail + '<br/>';
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

    }

})();