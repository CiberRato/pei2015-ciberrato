/***********************
 * Swamp Dragon setup
 ***********************/
swampdragon.ready(function () {
    subscribe();
});


function subscribe () {
    swampdragon.subscribe('notifications', 'notifications', null, function (context, data) {
        // any thing that happens after successfully subscribing
        console.log("// any thing that happens after successfully subscribing");
    }, function (context, data) {
        // any thing that happens if subscribing failed
        console.log("// any thing that happens if subscribing failed");
    });
}


swampdragon.onChannelMessage(function (chanel, data) {
    console.log(data.data.message);
});
