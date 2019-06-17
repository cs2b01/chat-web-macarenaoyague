function getData(){
        var username = $('#username').val();
        var password = $('#password').val();
        var message = JSON.stringify({
                "username": username,
                "password": password
            });

        $.ajax({
            url:'/authenticate',
            type:'POST',
            contentType: 'application/json',
            data : message,
            dataType:'json',
            error: function(response){
            if(response['status']==401)
                return alert('Inc');
            if(response['status']==200)
                window.location.href = "http://127.0.0.1:8080/static/chat.html"

            }
        });
    }
