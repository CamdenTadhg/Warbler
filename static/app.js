const $likesButton = $('#likes-button');
const $thumbsUpIcon = $('.fa-thumbs-up');
const $messageArea = $('.message-area');
const $alertSpace = $('#alert-space');
const $userLink = $('#current-user-link');
const $newMessageLink = $('#new-message-link');

//event listener for clicking like/unlike button
$likesButton.on('click', async function(event){
    event.preventDefault();
    console.log('like button clicked');
    console.log('msg_id should be:');
    console.log($(event.currentTarget).closest('li').attr('id'));
    const msg_id = $(event.currentTarget).closest('li').attr('id');
    const new_like = new Like(msg_id)
    let response = await new_like.addremoveLike();
    console.log('response = ', response);
    if (response == 'like added'){
        console.log('like added if')
        $(event.currentTarget).removeClass('btn-secondary')
        $(event.currentTarget).addClass('btn-primary');
        console.log($(event.currentTarget).attr('class'))
    }
    else if (response == 'like removed'){
        console.log('like removed if')
        $(event.currentTarget).removeClass('btn-primary')
        $(event.currentTarget).addClass('btn-secondary');
    }
    else if (response == 'request failed'){
        $alertSpace.text("Request failed. Please try again");
    }
})

//event listener for clicking thumbs up icon
$thumbsUpIcon.on('click', async function(event){
    event.preventDefault();
    console.log('thums up icon clicked');
    console.log('msg_id should be:');
    console.log($(event.currentTarget).closest('li').attr('id'));
    const msg_id = $(event.currentTarget).closest('li').attr('id');
    const new_like = new Like(msg_id)
    let response = await new_like.addremoveLike();
    console.log('response = ', response);
    if (response == 'like added'){
        console.log('like added if')
        console.log(event.currentTarget.parentNode)
        $(event.currentTarget.parentNode).removeClass('btn-secondary')
        $(event.currentTarget.parentNode).addClass('btn-primary');
        console.log($(event.currentTarget).attr('class'))
    }
    else if (response == 'like removed'){
        console.log('like removed if')
        console.log(event.currentTarget.parentNode)
        $(event.currentTarget.parentNode).removeClass('btn-primary')
        $(event.currentTarget.parentNode).addClass('btn-secondary');
    }
    else if (response == 'request failed'){
        $messageSpace.text("Request failed. Please try again");
    }
})

//event listener for clicking add message link