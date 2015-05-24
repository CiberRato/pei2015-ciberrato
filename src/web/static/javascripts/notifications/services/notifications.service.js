(function () {
    'use strict';

    angular
        .module("ciberonline.notifications.services")
        .factory("Notification", Notification);

    Notification.$inject = ["$dragon"];

    function Notification($dragon){
        var Notification = {
            activateNotifications: activateNotifications
        };

        return Notification;

        function activateNotifications(){
            $dragon.onChannelMessage(function(channels, data) {
                console.log("HOME");
                if(data.data._type != 'streamtrial'){
                    if (data.data.message.status == 200){
                        $.jGrowl(data.data.message.content, {
                            life: 3500,
                            theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                        });
                    }else if(data.data.message.status == 400){
                        $.jGrowl(data.data.message.content, {
                            life: 3500,
                            theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                        });
                    }else if(data.data.message.status == 100){
                        $.jGrowl(data.data.message.content, {
                            life: 3500,
                            theme: 'jGrowl-notification ui-state-highlight ui-corner-all info'
                        });
                    }
                    // console.log(channels);
                    console.log(data.data._type);
                    console.log(data.data.message);
                }else{
                    // tratar aqui do stream
                }
            });
        }
    }
})();