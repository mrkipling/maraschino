function ajax_call(url){
    $.ajax(
    {
        type: 'GET',
        url: url,
        beforeSend: function ()
        {
            // this is where we append a loading image
        },
        success: function (data)
        {
            // successful request; do something with the data
            //alert(data);
        },
        error: function ()
        {
            // failed request; give feedback to user
            alert("Sorry, but I couldn't create an XMLHttpRequest");
        }
    });
}