$(document).ready(function(){
  $('#search').keyup(function(){

    if($('#search').val() != ""){
      $.ajax({
        url: '/on_search',
        method: 'POST',
        data: { "search_term": $('#search').val()}
      })
      .done(function(response){
        $("#result").html(response);
      })
    }
  })
})
