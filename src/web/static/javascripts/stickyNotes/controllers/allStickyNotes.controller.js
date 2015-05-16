(function(){

    'use strict';

    angular
        .module('ciberonline.stickyNotes.controllers')
        .controller('AllStickyNotesController', AllStickyNotesController);

    AllStickyNotesController.$inject = ['StickyNotes', '$scope', '$timeout'];

    function AllStickyNotesController(StickyNotes, $scope, $timeout){
        var vm = this;
        vm.edit = edit;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            StickyNotes.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.stickyNotes = data.data;
                console.log(vm.stickyNotes);
                $scope.loader = {
                    loading: true
                };
            }

            function getAllErrorFn(data){
                console.error(data.data);
            }

        }

        function edit(identifier, text, time){
            StickyNotes.edit(identifier, text, time).then(editSuccessFn, editErrorFn);

            function editSuccessFn(){
                $.jGrowl("Sticky Note has been updated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    StickyNotes.getAll().then(getAllSuccessFn, getAllErrorFn);

                    function getAllSuccessFn(data){
                        vm.stickyNotes = data.data;
                        console.log(vm.stickyNotes);
                        $scope.loader = {
                            loading: true
                        };
                    }

                    function getAllErrorFn(data){
                        console.error(data.data);
                    }                });
            }

            function editErrorFn(data){
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