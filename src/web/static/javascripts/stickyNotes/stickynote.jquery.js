$(document).ready(function(){
    $.getJSON("/api/v1/sticky_notes/active/", function(data) {
        var notes = data;
        var i = -1;

        if(notes.length>1){
            setTimeout(function changeNote() {
                if(notes.length-1 <= i){
                    i = 0;
                }else{
                    i = i+1;
                }

                $(".side-note-container").html(notes[i].note);
                setTimeout(changeNote, notes[i].time*1000);
            }, 0);
        }else if(notes.length==1){
            $(".side-note-container").html(notes[0].note);
        }else{
            $(".side-note-container").html("There are any note to show!");
        }
    });
});