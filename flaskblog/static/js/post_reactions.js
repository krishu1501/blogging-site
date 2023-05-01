async function sendReaction(url, body){
    const resp = await fetch(url,{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: body
    });
    if(resp.redirected){
        // window.location.replace(resp.url);
        throw "Redirected!";
    }
    if(resp.status<200 || resp.status>299){
            throw "Error, Response code: "+resp.status;
    }
    return resp.json();
}

function updateButtonsWrapper(id, likesClassName, dislikesClassName, hasLiked, buttonSelectedClass){
    let prevReaction = 0; // 2 -> had liked previously , 1 -> had disliked previously ,0 -> no prev reaction 
    if(document.getElementById(id).querySelector("button[title='Like']").classList.contains(buttonSelectedClass)){
        prevReaction |= 2;
    }
    else if(document.getElementById(id).querySelector("button[title='Dislike']").classList.contains(buttonSelectedClass)){
        prevReaction |= 1;
    }
    function updateButtons(json){
        const postElement = document.getElementById(id);
        postElement.getElementsByClassName(likesClassName)[0].innerHTML = json.likes;
        postElement.getElementsByClassName(dislikesClassName)[0].innerHTML = json.dislikes;
        if(hasLiked && (prevReaction===1 || prevReaction===0)){
            postElement.querySelector("button[title='Like']").classList.add(buttonSelectedClass);
            postElement.querySelector("button[title='Dislike']").classList.remove(buttonSelectedClass);
        }
        else if(!hasLiked && (prevReaction===2 || prevReaction===0)){
            postElement.querySelector("button[title='Like']").classList.remove(buttonSelectedClass);
            postElement.querySelector("button[title='Dislike']").classList.add(buttonSelectedClass);
        }
        else{
            postElement.querySelector("button[title='Like']").classList.remove(buttonSelectedClass);
            postElement.querySelector("button[title='Dislike']").classList.remove(buttonSelectedClass);
        }
    }
    return updateButtons;
}

function reactOnPost(url, postId, hasLiked, loginUrl, isLoggedIn){
    if(!isLoggedIn){
        window.location.replace(loginUrl);
    }
    data = {post_id: postId, has_liked: hasLiked};
    const updateButtons = updateButtonsWrapper('post-'+postId, 'likes-count', 'dislikes-count', hasLiked, 'btn-primary');
    sendReaction(url, JSON.stringify(data)).then(updateButtons).catch((err) => console.log(err));
}