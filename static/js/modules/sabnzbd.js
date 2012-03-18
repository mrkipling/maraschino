/********* START SABNZBD ***********/

$(document).on('click', '#sabnzbd .inner #status', function(){
  var state = false;
  if($(this).attr('status').toLowerCase() === 'true'){
    //queue is paused
    state = 'resume';
  } else {
    state = 'pause';
  }
  $.get('/xhr/sabnzbd/queue/'+state+'/')
  .success(function(data){
    if(data.status === 'true'){
      get_module('sabnzbd');
    }
  })
  .error('Could not reach Maraschino');
});

/********* END SABNZBD ***********/
