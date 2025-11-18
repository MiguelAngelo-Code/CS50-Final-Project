
function startEdit(id) {
   
    // todo:
    // Account 
    // Type
    // Category
    // Date

    // Amount
    document.getElementById(`view-amt-${id}`).style.display = "none";
    document.getElementById(`edit-amt-${id}`).style.display = "inline-block";

    // Buttons
    document.getElementById(`edit-btn-${id}`).style.display = "none";
    document.getElementById(`save-btn-${id}`).style.display = "inline-block";
}

// todo cancle edit function