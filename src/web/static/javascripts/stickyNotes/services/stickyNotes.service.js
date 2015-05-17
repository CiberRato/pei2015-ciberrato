(function () {
    'use strict';

    angular
        .module("ciberonline.stickyNotes.services")
        .factory("StickyNotes", StickyNotes);

    StickyNotes.$inject = ['$http'];

    function StickyNotes($http) {
        var StickyNotes = {
            getAll: getAll,
            create: create,
            edit: edit,
            remove: remove,
            toggle: toggle
        };

        return StickyNotes;

        function getAll() {
            return $http.get('/api/v1/sticky_notes/crud/');
        }

        function create(text, time){
            return $http.post('/api/v1/sticky_notes/crud/', {
                time: time,
                note: text
            });
        }

        function edit(identifier, text, time){
            return $http.put("/api/v1/sticky_notes/crud/" + identifier + "/", {
                note: text,
                time: time
            })
        }

        function remove(identifier){
            return $http.delete("/api/v1/sticky_notes/crud/" + identifier + "/");
        }

        function toggle(identifier){
            return $http.post('/api/v1/sticky_notes/toggle/', {
                identifier: identifier
            });
        }

    }

})();
