(function (){
    'use strict';

    angular
        .module('ciberonline.grid', [
            'ciberonline.grid.controllers',
            'ciberonline.grid.services'
        ]);

    angular
        .module('ciberonline.grid.controllers', []);

    angular
        .module('ciberonline.grid.services', ['ngCookies']);
})();