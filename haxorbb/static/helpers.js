function get_post_elements() {
    return $('.content');
}

function process_twitter_urls(elems){
    $.each(elems, function(i, e){
        var links = $(this).find("a");
        $.each(links, function (i, l){
            if (/:\/\/twitter.com\//.test(l.innerHTML)) {
                var id_ = l.innerHTML.split('/').pop();
                var parent = $(l).parent();
                parent.html('<p></p>');
                var p = parent.find("p");
                twttr.widgets.createTweet(id_, parent[0], {maxwidth:500});
            }
        })

    });
}

function process_youtube_urls(elems) {
    $.each(elems, function(){
        var links = $(this).find("a");
        $.each(links, function(i, v) {
            var video_id;
            if (/:\/\/(?:www\.)?youtube\.com/.test(v.innerHTML)) {
                video_id = v.innerHTML.split('=').pop();
            } else if (/:\/\/youtu\.be\//.test(v.innerHTML)) {
                video_id = v.innerHTML.split('/').pop();
            }
            if (video_id != undefined) {
                var parent = $(v).parent();
                parent.addClass('ytplayer');
                $(parent).html('<iframe id="player" type="text/html" width="640" height="390"' +
                    'src="https://www.youtube.com/embed/'+video_id+'?enablejsapi=1" frameborder="0"></iframe>');
            }
            video_id = null;
        });
    })
}
