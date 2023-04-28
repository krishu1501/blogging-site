function preview_pic(picture_name, picture_path){
    element = document.getElementById('profile-pic');
    element.src = picture_path;
    document.getElementById('predef_picture').value = picture_name;
}

function clear_current_image_selection(original_picture_path){
    document.getElementById('profile-pic').src = original_picture_path;
    document.getElementById('predef_picture').value = "";
    document.getElementById('picture').value = "";
}

function toggle_image_change_section(original_picture_path){
    document.getElementById('image-change-section').hidden = !document.getElementById('image-change-section').hidden; 
    clear_current_image_selection(original_picture_path);
}
function toggle_image_change_option(original_picture_path){
    if(document.getElementById('upload-profile-pic').hidden){
        document.getElementById('upload-profile-pic').hidden = false;
        document.getElementById('select-from-profile-pics').hidden = true;
    }
    else{
        document.getElementById('upload-profile-pic').hidden = true;
        document.getElementById('select-from-profile-pics').hidden = false;        
    }
    clear_current_image_selection(original_picture_path);
}