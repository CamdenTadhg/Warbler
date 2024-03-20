const $likesButton = $('#likes-button');
const $thumbsUpIcon = $('.fa-thumbs-up');
const $messageArea = $('.message-area');
const $alertSpace = $('#alert-space');
const $userLink = $('#current-user-link');
const $newMessageLink = $('#new-message-link');
const $Modal = $('#newMessageModal');
const $addWarble = $('#add-warble');
const $dismissModal = $('#dismiss-modal');
const $closeButton = $('.btn-close');
const $modalBody = $('.modal-body');
const $container = $('.container');

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
    if (response === 'like added'){
        console.log('like added if')
        console.log(event.currentTarget.parentNode)
        $(event.currentTarget.parentNode).removeClass('btn-secondary')
        $(event.currentTarget.parentNode).addClass('btn-primary');
        console.log($(event.currentTarget).attr('class'))
    }
    else if (response === 'like removed'){
        console.log('like removed if')
        console.log(event.currentTarget.parentNode)
        $(event.currentTarget.parentNode).removeClass('btn-primary')
        $(event.currentTarget.parentNode).addClass('btn-secondary');
    }
    else if (response === 'request failed'){
        $alertSpace.text("Request failed. Please try again");
        $alertSpace.show()
    }
})

// event listener for adding new messages
$addWarble.on('click', async function(event){
    event.preventDefault();
    console.log('add warble button clicked');
    const msg_text = $('#message-text').val();
    console.log(msg_text);
    let response = await Message.addMessage(msg_text);
    $('#message-text').val('');
    console.log(response);
    if (response === 'message created'){
        $messageCreated = $('<div class="alert alert-success" id="message-created">Message created</div>');
        $modalBody.prepend($messageCreated);
    }
})

// event listener for canceling modal
$dismissModal.on('click', function(event){
    $('#message-text').val('')
    $('#message-created').remove()
})

// event listener for closing modal
$closeButton.on('click', function(event){
    $('#message-text').val('')
    $('#message-created').remove()
})