$( document ).ready(function() {

    $("#in_text").on("input", function() {

        send_ajax($(this).val())
    });

    function send_ajax(input_data){

        $.ajax({
            type: 'POST',
            url: URL,
            dataType: 'json',
            data:{
                'csrfmiddlewaretoken':CSRF_TOKEN,
                'text':input_data
                },
            success: function(res) {
                console.log(res);
                show_emails(res)
            }
        });
    }
    
    function show_emails(data){
        my_ul_tag = $('#mu_ul')
        my_ul_tag.empty()
        if ( data['emails'] ){
            for (const [key, value] of Object.entries(data['emails'])) {
                console.log("*", key, value);
                var li = document.createElement("li");
                var a = document.createElement('a');
                  var linkText = document.createTextNode(value);
                  a.appendChild(linkText);
                  a.title = value;
                  a.href = URL2;
                  li.append(a)
                    my_ul_tag.append(li)
              }
            
        }else{
            my_ul_tag.append()
        }
        
    }
  });