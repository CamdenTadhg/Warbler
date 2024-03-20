
class Message {

    constructor(text){
        this.text = text
    }

    static async addMessage(text){
        try {
            console.log('starting add message');
            console.log(text)
            const response = await axios.post('/messages/new', {'text': `${text}`});
            console.log(response);
            return response.data;
        }catch(error){
            $error = $('<div class="alert alert-danger">Message add failed</div>')
            $modalBody.prepend($error)
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
            $error = $('<div class="alert alert-danger">Like failed</div>')
            $container.prepend($error)
        }
    }
}


// write tests for all javascript functions

