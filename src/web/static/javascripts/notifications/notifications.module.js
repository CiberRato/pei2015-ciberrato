(function (){
    'use strict';

    angular
        .module('ciberonline.notifications', [
            'ciberonline.notifications.controllers',
            'ciberonline.notifications.services'
        ]);

    angular
        .module('ciberonline.notifications.controllers', []);

    angular
        .module('ciberonline.notifications.services', ['ngCookies']);
})();