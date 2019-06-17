function checkData(){
    alert(8);
    var name = $('#name').val();
    var fullname = $('#fullname').val();
    var username = $('#username').val();
    var password = $('#password').val();
    var country = $('#country option:selected').text();
    if (name=='')
    {
         return alert(JSON.stringify("Please check the required fields."));
    }
    if (fullname=='')
    {
         return alert(JSON.stringify("Please check the required fields."));
    }
    if (username=='')
    {
         return alert(JSON.stringify("Please check the required fields."));
    }
    if (password=='')
    {
         return alert(JSON.stringify("Please check the required fields."));
    }
    if (country=='-Seleccionar-')
    {
         return alert(JSON.stringify("Please check the required fields."));
    }
    var message = JSON.stringify({
            "name": name,
            "fullname": fullname,
            "username": username,
            "password": password,
            "country": country
    });
    $.ajax({
            url:'/users',
            type:'GET',
            contentType: 'application/json',
            dataType:'json',
            success: function(response){
                alert(1);
                var i = 0;
                $.each(response, function(){
                    if (response[i].username==username)
                        return alert(JSON.stringify("Please pick another username."));
                    i = i +  1;
                });
                $.ajax({
                        url:'/createUser',
                        type:'POST',
                        contentType: 'application/json',
                        data : message,
                        dataType:'json',
                        success: function(response){
                            alert(JSON.stringify(response));
                        },
                        error: function(response){
                          if(response["status"]==401){
                                alert("Try again");
                            }else{
                                alert("Your account has been successfully registered. Welcome to Global Chat Web.");
                                window.location.href = "http://0.0.0.0:8020/static/login.html";
                            }
                        }
                    });
            },
        });
}

