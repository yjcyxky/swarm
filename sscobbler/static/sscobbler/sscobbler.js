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