(function () {
    'use strict';

    angular
        .module("ciberonline.notifications.services")
        .factory("Notification", Notification);

    Notification.$inject = ["$dragon"];

    function Notification($dragon){
        var events = (function(){
          var topics = {};
          var hOP = topics.hasOwnProperty;

          return {
            subscribe: function(topic, listener) {
              // Create the topic's object if not yet created
              if(!hOP.call(topics, topic)) topics[topic] = [];

              // Add the listener to queue
              var index = topics[topic].push(listener) -1;

              // Provide handle back for removal of topic
              return {
                remove: function() {
                  delete topics[topic][index];
                }
              };
            },
            publish: function(topic, info) {
              // If the topic doesn't exist, or there's no listeners in queue, just leave
              if(!hOP.call(topics, topic)) return;

              // Cycle through topics queue, fire!
              topics[topic].forEach(function(item) {
                    item(info != undefined ? info : {});
              });
            }
          };
        })();

        var Notification = {
            events: events,
            activateNotifications: activateNotifications
        };

        return Notification;

        function activateNotifications(){
            $dragon.onReady(function() {
                swampdragon.open(function () {
                    $dragon.onChannelMessage(function (channels, data) {
                        events.publish(data.data._type, data.data);
                        console.log(data.data._type);
                    });
                });
            });
        }


    }
})();