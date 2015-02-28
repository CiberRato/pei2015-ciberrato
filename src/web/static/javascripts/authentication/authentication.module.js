(function (){
    'use strict';

    angular
        .module('ciberonline.authentication', [
            'ciberonline.authentication.controllers',
            'ciberonline.authentication.services'
        ]);

    angular
        .module('ciberonline.authentication.controllers', []);

    angular
        .module('ciberonline.authentication.services', ['ngCookies']);
})();