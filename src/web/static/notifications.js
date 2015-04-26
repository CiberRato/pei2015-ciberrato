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

/*
var swampDragon = null;

function onSubscribe(data) {
    console.log('subscribed to ' + data.channel_data.local_channel);
}

function onOpen(data) {
    console.log('open');
    swampDragon.subscribe('notifications', {}, 'onSubscribe', 'notifications');
}

function onChannelMessage(channel, message) {
    console.log(message.data);
}

function onClose(data) {
    console.log('closed');
}

function onMessage(message) {
    if ('client_callback_name' in message.data.context) {
        if (message.data.context.client_callback_name == 'onSubscribe') {
            onSubscribe(message.data);
        }
    }
}

$(function() {

    swampDragon = SwampDragon({
        onchannelmessage: onChannelMessage,
        onmessage: onMessage,
        onopen: onOpen
    });
    swampDragon.connect('http://' + window.location.hostname + ':9999', 'data');
});

/*

function enableInputs() {
    console.log("SUBSCRIBED!");
}

function disableInputs() {
    console.log("UNSUBSCRIBED!");
}

disableInputs();

swampdragon.open(function () {
    swampdragon.subscribe('notifications', 'notifications', function () {
        enabledInputs();
    });
});

swampdragon.close(function () {
    disableInputs();
});

swampdragon.onChannelMessage(function (channels, message) {
  for(var i in channels) {
      console.log(channels[i]);
      console.log(message.data);
      console.log("-----------");
  }
});

/*
// Ask the browser for permission to show notifications
// Taken from https://developer.mozilla.org/en-US/docs/Web/API/Notification/Using_Web_Notifications
window.addEventListener('load', function () {
    Notification.requestPermission(function (status) {
        // This allows to use Notification.permission with Chrome/Safari
        if (Notification.permission !== status) {
            Notification.permission = status;
        }
    });
});


// Create an instance of vanilla dragon
var dragon = new VanillaDragon({onopen: onOpen, onchannelmessage: onChannelMessage});

// This is the list of notifications
var notificationsList = document.getElementById("notifications");


// New channel message received
function onChannelMessage(channels, message) {
    // Add the notification
    addNotification((message.data));
}


// SwampDragon connection open
function onOpen() {
    // Once the connection is open, subscribe to notifications
    dragon.subscribe('notifications', 'notifications');
}


// Add new notifications
function addNotification(notification) {
    // If we have permission to show browser notifications
    // we can show the notifiaction
    if (window.Notification && Notification.permission === "granted") {
        new Notification(notification.message);
    }

    // Add the new notification
    var li = document.createElement("li");
    notificationsList.insertBefore(li, notificationsList.firstChild);
    li.innerHTML = notification.message;

    // Remove excess notifications
    while (notificationsList.getElementsByTagName("li").length > 5) {
        notificationsList.getElementsByTagName("li")[5].remove();
    }
}
*/
