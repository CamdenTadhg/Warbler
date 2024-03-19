class Message {

    constructor(id, text, user_id){
        this.id = id
        this.text = text
        this.user_id = user_id
    }

    async addremoveLike(msg_id){
        try{
            console.log('starting addremoveLike');
            const response = await axios.post(`/users/add_like/${msg_id}`);
            console.log(response);
            return response;
        } catch(error) {
            alert("Like failed. Please try again.")
        }
    }

    async addMessage(){}

}

// create event listener for liking/unliking and changing the button
// see if it works
// fix it until it works
// create addMessage function
// revise view function to accept data from addMessage function and return appriopriate response
// create event listener for creating new message on the link
// create modal in which to create a new message
// create event listener on the modal to submit addMessage
// write tests for all these functions. 