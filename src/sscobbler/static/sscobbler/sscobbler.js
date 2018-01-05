function loadurl(url) {
  $.ajax({
    url: url,
    success: function(ret){
      $('#content').html(ret);
    },
    dataType: 'html'
  });

  if($('#welcome').is(':visible')){
    $('#welcome').css("display", "none");
  }
  $('#content').css("display", "block")
}

/* show tasks not yet recorded, update task found time in hidden field */
function get_latest_task_info(ip_address) {
  var username = document.getElementById("username").value

  /* FIXME: used the logged in user here instead */
  /* FIXME: don't show events that are older than 40 seconds */

  $.getJSON("http://" + ip_address + "/cblr/svc/op/events/user/" + username,
    function(data){$.each(data, function(i,record) {
      var id = record[0];
      var ts = record[1];
      var name = record[2];
      var state = record[3];
      var buf = ""
      var logmsg = " <a href=javascript:loadurl(\"/sscobbler/eventlog/" + id + "\")>(log)</a>";
      if (state == "complete") {
        buf = "Task " + name + " is complete: " + logmsg;
      }
      else if (state == "running") {
        buf = "Task " + name + " is running: " + logmsg;
      }
      else if (state == "failed") {
        buf = "Task " + name + " has failed: " + logmsg;
      }
      else {
        buf = name;
      }
      window.status = buf;
      var js_growl = new jsGrowl('js_growl');
      js_growl.addMessage({msg:buf});
    });
  });
}

function _get_latest_task_info(ip_address) {
  return function() {
    get_latest_task_info(ip_address);
  }
}

function page_onload() { 
  var submitting = false;

  $(window).bind("submit", function () {

    submitting = true;

  });

  $(window).bind("beforeunload", function () {

    if (!submitting && $("#aidata")[0].defaultValue !== $("#aidata")[0].value) {

      submitting = false;
      return "You have unsaved changes.";
    }

  });
}