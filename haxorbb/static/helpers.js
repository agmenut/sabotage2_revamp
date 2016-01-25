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

function process_youtube_urls() {
    var links = $(document).find('#content').find('a');
    $.each(links, function(i, v){
        var a = v.href.match(/(?:.*youtube\.com\/watch\?v=|.*youtu\.be\/)([a-zA-Z0-9\-]*)/);
        var video_id;
        if (a && a[1]){
            video_id = a[1];
            var d = v.ownerDocument;
            var p = d.createElement('p');
            var v_container = d.createElement('div');
            v_container.id = 'ytplayer_' + video_id;
            p.appendChild(v_container);
            v.parentNode.insertBefore(p, v.nextSibling);
            player = new YT.Player('ytplayer_' + video_id, {
                height: '405',
                width: '720',
                videoId: video_id,
                controls: 1,
                events: {
                    onStateChange: onPlayerStateChange
                }
            });
        }
    });
}


function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.PLAYING) {
        event.target.setPlaybackQuality('hd720');
    }
}