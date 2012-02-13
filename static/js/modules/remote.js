/*********** REMOTE *************/

var remote = false;
var remote_connected = false;
var remote_connection;
// Activates remote functions
function send_key(key){
  $.get('/remote/'+key)
  .success(function(data){
    if(data.error){
      popup_message(data.error);
    }
  })
  .error(function(){
    popup_message('Could not reach Maraschino');
  });
}

$(document).on('click', '#remote_icon', function(){
  $(this).toggleClass('on');
  if(remote){
    remote = false;
    remote_connected = false;
    $.get('/remote/close');
    clearInterval(remote_connection);
  } else {
    remote = true;
    remote_connected = true;
    $.get('/remote/connect');
    remote_connection = setInterval(function(){$.get('/remote/ping');}, 59000);
  }
  if(remote){
    $(document).on('keydown', 'body' , function(e){
      e.preventDefault();
      var char = '';
      var keyCodeMap = {8:"backspace", 9:"tab", 13:"return", 16:"shift", 17:"ctrl", 18:"alt", 19:"pausebreak", 20:"capslock", 27:"escape", 32:"space",
          33:"pageup", 34:"pagedown", 35:"end", 36:"home", 37:"left", 38:"up", 39:"right", 40:"down", 43:"plus", 44:"printscreen", 45:"insert", 46:"delete",
          48:"0", 49:"1", 50:"2", 51:"3", 52:"4", 53:"5", 54:"6", 55:"7", 56:"8", 57:"9", 59:"semicolon", 61:"plus", 65:"a", 66:"b", 67:"c", 68:"d", 69:"e",
          70:"f", 71:"g", 72:"h", 73:"i", 74:"j", 75:"k", 76:"l", 77:"m", 78:"n", 79:"o", 80:"p", 81:"q", 82:"r", 83:"s", 84:"t", 85:"u", 86:"v", 87:"w",
          88:"x", 89:"y", 90:"z", 96:"0", 97:"1", 98:"2", 99:"3", 100:"4", 101:"5", 102:"6", 103:"7", 104:"8", 105:"9", 106: "*", 107:"plus", 109:"minus",
          110:"period", 111: "forwardslash", 112:"f1", 113:"f2", 114:"f3", 115:"f4", 116:"f5", 117:"f6", 118:"f7", 119:"f8", 120:"f9", 121:"f10", 122:"f11",
          123:"f12", 144:"numlock", 145:"scrolllock", 186:"semicolon", 187:"plus", 188:"comma", 189:"minus", 190:"period", 191:"forwardslash", 192:"tilde",
          219:"openbracket", 220:"backslash", 221:"closebracket", 222:"singlequote"};
      if (e.which == null){
        char= String.fromCharCode(e.keyCode);    // old IE
      } else {
        char = keyCodeMap[e.which];
      }
      send_key(char);
    });
  } else {
    $(document).off('keydown', 'body');
  }
});
/********* END REMOTE ***********/
