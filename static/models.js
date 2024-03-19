
class Message {

    constructor(id, text, user_id){
        this.id = id
        this.text = text
        this.user_id = user_id
    }

    async addMessage(){
        try {
            console.log('starting add message');
            const response = await axios.post('/messages/new', messageData)
            console.log(response);
        }catch(error){
            $alertSpace.text('Request failed. Please try again.')
        }
    }
}

class Like {

    constructor(msg_id){
        this.msg_id = msg_id
    }

    async addremoveLike(){
        try{
            console.log('starting addremoveLike');
            const response = await axios.post(`/users/add_like/${this.msg_id}`);
            console.log('response.data = ', response.data);
            return response.data;
        } catch(error) {
            $alertSpace.text("Request failed. Please try again")
        }
    }
}


// create modal in which to create a new message (put the form in it)
// create event listener on the modal to submit addMessage
// make sure it works
// fix likes functionality now that I added the bootstrap javascript which apparently broke it
// fix likes page doing the likes button incorrectly
// write tests for all javascript functions

