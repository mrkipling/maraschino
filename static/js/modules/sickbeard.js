/*** SICKBEARD ***/

// Search Episode Functionality on Magnifying Glass png

$(document).on('click', '#sickbeard .coming_ep div.options img.search', function(){
  $(this).attr('src','/static/images/xhrloading.gif');
  var ep = $(this).attr('episode');
  var season = $(this).attr('season');
  var id = $(this).attr('id');
  $.get('/sickbeard/search_ep/'+id+'/'+season+'/'+ep)
  .success(function(data){
  if(data){
    $('#sickbeard #'+id+'_'+season+'_'+ep+' div.options img.search').attr('src','/static/images/yes.png');
  } else {
    $('#sickbeard #'+id+'_'+season+'_'+ep+' div.options img.search').attr('src','/static/images/no.png');
  }
  })
  .error(function(){
    popup_message('Could not reach Sick-Beard.');
  });
});

// Air time on hover

$(document).on('hover', '#sickbeard .coming_ep', function(){
  var id = ($(this).attr('id'));
});


// Load show info from banner display

$(document).on('click', '#sickbeard .coming_ep .options img.banner', function(){
  var tvdb = $(this).attr('id');
  $.get('/sickbeard/get_show_info/'+tvdb, function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Plot display function

$(document).on('mouseenter', '#sickbeard .coming_ep .details .plot-title', function(){
  $(this).toggle();
  var id = $(this).closest('div.coming_ep').attr('id');
  $('#sickbeard #'+id+' .details .plot').toggle();
});

// Plot hide function

$(document).on('mouseleave', '#sickbeard .coming_ep', function(){
  var id = $(this).attr('id');
  $('#sickbeard #'+id+' .details .plot-title').show();
  $('#sickbeard #'+id+' .details .plot').hide();
});

// Toggle missed episodes

$(document).on('click', '#sickbeard #missed', function(){
  $('#sickbeard .missed').toggle();
});

// All Shows menu

$(document).on('click', '#sickbeard .menu .all', function(){
  $.get('/sickbeard/get_all', function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Coming episodes Menu

$(document).on('click', '#sickbeard .menu .upcoming', function(){
  $.get('/xhr/sickbeard', function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// History menu

$(document).on('click', '#sickbeard .menu .history', function(){
  $.get('/sickbeard/history/30', function(data){
    $('#sickbeard').html($(data).html());
  });
});

$(document).on('click', '#sickbeard .history ul.toggle', function(){
  $('#sickbeard .history .Snatched').toggle();
  $(this).toggleClass('active');
});

// Show Menu

$(document).on( 'click', '#sickbeard .menu-icon', function(){
  $('#sickbeard .menu').fadeToggle(200);
});

// Show info

$(document).on('click', '#sickbeard #sickbeard-list ul', function(){
  var id = $(this).attr('id');
  $.get('/sickbeard/get_show_info/'+id, function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Episode list back button functionality

$(document).on('click', '#sb_content > #show .sb-back', function(){
  $.get('/sickbeard/get_all', function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Season info

$(document).on('click', '#sb_content > #show ul.seasons li', function(){
  $.get('/sickbeard/get_season/'+$(this).attr('tvdbid')+'/'+$(this).attr('season'), function(data){
    $('#sickbeard').replaceWith(data);
    $('#sickbeard .episode-list .tablesorter').tablesorter({sortList: [[0,0]]});
  });
});

// Going into episode info

$(document).on('click', '#sickbeard .episode-list #season tbody tr', function(){
  $.get('/sickbeard/get_ep_info/'+$(this).attr('link'), function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Episode info back button functionality

$(document).on('click', '#sickbeard .episode-info .back', function(){
  $.get('/sickbeard/get_season/'+$(this).attr('tvdbid')+'/'+$(this).attr('season'), function(data){
    $('#sickbeard').replaceWith(data);
    $('#sickbeard .episode-list .tablesorter').tablesorter({sortList: [[0,0]]});
  });
});

// Back Button Episode List

$(document).on('click', '#sickbeard .episode-list >.back', function(){
  $.get('/sickbeard/get_show_info/'+$(this).attr('tvdbid'), function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Show Banner manager display

$(document).on('click', '#sickbeard #show .banner .options' , function(){
  $('#sickbeard #show .banner .manage').show();
});

// Hide Banner manager display

$(document).on('click', '#sickbeard #show .banner .manage .close' , function(){
  $('#sickbeard #show .banner .manage').hide();
});

//Delete show function

$(document).on('click', '#sickbeard #show .banner .manage .delete' , function(){
  var id = $('#sickbeard #show .banner .manage').attr('tvdbid')
  $.get('/sickbeard/delete_show/'+id)
  .success(function(data){
    popup_message(data);
  })
  .error(function(){
    popup_message('Could not reach Sickbeard.');
  });
});

//Refresh show function

$(document).on('click', '#sickbeard #show .banner .manage .refresh' , function(){
  var id = $('#sickbeard #show .banner .manage').attr('tvdbid')
  $.get('/sickbeard/refresh_show/'+id)
  .success(function(data){
    popup_message(data);
  })
  .error(function(){
    popup_message('Could not reach Sickbeard.');
  });
});

//Update show function

$(document).on('click', '#sickbeard #show .banner .manage .update' , function(){
  var id = $('#sickbeard #show .banner .manage').attr('tvdbid')
  $.get('/sickbeard/update_show/'+id)
  .success(function(data){
    popup_message(data);
  })
  .error(function(){
    popup_message('Could not reach Sickbeard.');
  });
});

// Shutoff function

$(document).on('click', '#sickbeard div.powerholder .power', function(){
  $.get('/sickbeard/shutdown')
  .success(function(data){
    popup_message(data);
  })
  .error(function(){
    popup_message('Could not reach Sickbeard.');
  });
});

// Restart Function

$(document).on('click', '#sickbeard div.powerholder .restart', function(){
  $.get('/sickbeard/restart')
  .success(function(data){
    popup_message(data);
  })
  .error(function(){
    popup_message('Could not reach Sickbeard.');
  });
});

// Log function

$(document).on('click', '#sickbeard div.powerholder .log', function(){
  $.get('/sickbeard/log/error', function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Log info level change

$(document).on('change', '#sickbeard #log .level', function(){
  var level = $('#sickbeard #log .level').attr('value');
  $.get('/sickbeard/log/'+level, function(data){
    $('#sickbeard').replaceWith(data);
  });
});

// Load search template

$(document).on('click', '#sickbeard div.powerholder .add', function(){
  $.get('/sickbeard/search/')
  .success(function(data){
    $('#sickbeard').replaceWith(data);
  })
  .error(function(){
    popup_message('Could not reach Maraschino.');
  });
});

// Load search results

$(document).on('keypress', '#sickbeard #search #value', function(e){
  if(e.which == 13){
    e.preventDefault();
    var name = $('#sickbeard #search #value').attr('value');
    var type = $('#sickbeard #search #tvdbid').attr('value');
    var lang = $('#sickbeard #search #lang').attr('value');
    params = ''
    if(name != ''){
      if(type == 'name'){
        params = 'name='+name;
      } else {
        params = 'tvdbid='+name;
      }
      if(lang != ''){
        params = params + '&lang='+lang;
      }
    }
    $.get('/sickbeard/search/?'+params)
    .success(function(data){
      $('#sickbeard').replaceWith(data);
    })
    .error(function(){
popup_message('Could not reach Maraschino.');
    });
  }
});

// Add show function

$(document).on('click', '#sickbeard #search #result tr', function(){
  $.get('/sickbeard/add_show/'+$(this).attr('tvdbid'))
  .success(function(data){
    popup_message(data);
  })
  .error(function(data){
    popup_message('Could not reach Maraschino.');
  });
});

// Magnifying Glass Episode INFO

$(document).on('click', '#sickbeard .episode-info .status .search', function(){
  $(this).attr('src','/static/images/xhrloading.gif');
  var ep = $(this).attr('episode');
  var season = $(this).attr('season');
  var id = $(this).attr('id');
  $.get('/sickbeard/search_ep/'+id+'/'+season+'/'+ep)
  .success(function(data){
    if(data){
$('#sickbeard .episode-info .status .search').attr('src','/static/images/yes.png');
    } else {
      $('#sickbeard .episode-info .status .search').attr('src','/static/images/no.png');
    }
  })
  .error(function(){
    popup_message('There was a problem with Sick-Beard.');
  });
});

// Episode set status info

$(document).on('change', '#sickbeard .episode-info .status select', function(){
  var ep = $(this).attr('episode');
  var season = $(this).attr('season');
  var id = $(this).attr('id');
  var status = this.value;
  $.get('/sickbeard/set_ep_status/'+id+'/'+season+'/'+ep+'/'+status)
  .success(function(data){
    if (data.status !== 'success') {
      popup_message('An error ocurred: '+data);
    }
  })
  .error(function(){
    popup_message('There was a problem with Sick-Beard.');
  });
});

/******  END SICKBEARD Functions  *******/
