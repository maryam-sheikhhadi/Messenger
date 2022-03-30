function show_emails(data) {
    my_ul_tag = $('#mu_ul')
    my_ul_tag.empty()
    console.log("*", data);
    console.log("*%%%", data.emails);
    var emails = data.emails;
    if (emails) {
        for (const email in emails) {
            console.log("*", email.pk);
            console.log("*000", emails[email].pk);

            var li = document.createElement("li");
            var a = document.createElement('a');
            var linkText = document.createTextNode(emails[email].subject);
            a.appendChild(linkText);
            a.title = emails[email].subject;
            a.href = "/mail/mail-detail/" + emails[email].pk;
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
        url: "/mail/search_email/",
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': CSRF_TOKEN,
            'text': input_data
        },
        success: function (res) {
            show_emails(res)
        }
    });
}


$(document).ready(function () {

    $("#in_text").on("keyup", function () {

        send_ajax(this.value)
    });
});
