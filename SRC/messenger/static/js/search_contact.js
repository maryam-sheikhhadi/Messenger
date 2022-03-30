function show_contacts(data) {
    my_ul_tag = $('#mu_ul')
    my_ul_tag.empty()
    console.log("*", data);
    console.log("*%%%", data.contacts);
    var contacts = data.contacts;
    if (contacts) {
        for (const contact in contacts) {
            console.log("*000", contacts[contact].pk);

            var li = document.createElement("li");
            var a = document.createElement('a');
            var linkText = document.createTextNode(contacts[contact].first_name
                                                   + " " + contacts[contact].last_name
                                                    );
            a.appendChild(linkText);
            a.title =contacts[contact].first_name + " " + contacts[contact].last_name
            a.href = "/contacts/contact-detail/" + contacts[contact].pk;
            li.append(a)
            my_ul_tag.append(li)
        }

    } else {
        my_ul_tag.append()
    }

}


function send_ajax(input_data) {

    $.ajax({
        type: 'POST',
        url: "/contacts/search_contacts/",
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': CSRF_TOKEN,
            'text': input_data
        },
        success: function (res) {
            show_contacts(res)
        }
    });
}


$(document).ready(function () {

    $("#in_text").on("keyup", function () {

        send_ajax(this.value)
    });
});
