const $likesButton = $('#likes-button');

//event listener for pressing like/unlike button
$likesButton.click(function(event){
    event.preventDefault()
    console.log('like button clicked')
    console.log(event.target)
})