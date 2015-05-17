$(document).ready(function(){
    $.getJSON("/api/v1/sticky_notes/active/", function(data) {
        console.log(data);
        var notes = data;
        var i = 0;

        setTimeout(function changeNote() {
            $(".side-note-container").html(notes[i].note);
            if(notes.length-1 <= i){
                i = 0;
            }else{
                i = i+1;
            }
            setTimeout(changeNote, notes[i].time*1000);
        }, 0);
    });
});