

function startEdit(id) {
   
    // Hide/show <td> fileds

    // Account
    document.getElementById(`view-acc-${id}`).style.display = "none";
    document.getElementById(`edit-acc-${id}`).style.display = "inline-block";

    // Type
    document.getElementById(`view-type-${id}`).style.display = "none";
    document.getElementById(`edit-type-${id}`).style.display = "inline-block";

    // Category
    document.getElementById(`view-cat-${id}`).style.display = "none";
    document.getElementById(`edit-cat-${id}`).style.display = "inline-block";

    // Date
    document.getElementById(`view-date-${id}`).style.display = "none";
    document.getElementById(`edit-date-${id}`).style.display = "inline-block";

    // Amount
    document.getElementById(`view-amt-${id}`).style.display = "none";
    document.getElementById(`edit-amt-${id}`).style.display = "inline-block";

    // Hide delete/edit buttons
    document.getElementById(`del-btn-${id}`).style.display = "none";
    document.getElementById(`edit-btn-${id}`).style.display = "none";

    // Show save/cancel buttons
    document.getElementById(`save-btn-${id}`).style.display = "inline-block";
    document.getElementById(`cancel-btn-${id}`).style.display = "inline-block";

    // disable dropdown buttons outside of edit row
    var elements = document.getElementsByName('drop-btn');

    for (var i = 0; i < elements.length; i++){

        if (elements[i].id !== `drop-btn-${id}`){
            elements[i].disabled = true;
        } 
    }
}


// Cancle edit
function endEdit(id) {

    // Fields

    // Account
    document.getElementById(`view-acc-${id}`).style.display = "inline-block";
    document.getElementById(`edit-acc-${id}`).style.display = "none";

    // Type
    document.getElementById(`view-type-${id}`).style.display = "inline-block";
    document.getElementById(`edit-type-${id}`).style.display = "none";

    // Category
    document.getElementById(`view-cat-${id}`).style.display = "inline-block";
    document.getElementById(`edit-cat-${id}`).style.display = "none";

    // Date
    document.getElementById(`view-date-${id}`).style.display = "inline-block";
    document.getElementById(`edit-date-${id}`).style.display = "none";

    // Amount
    document.getElementById(`view-amt-${id}`).style.display = "inline-block";
    document.getElementById(`edit-amt-${id}`).style.display = "none";

    // Show delete/edit buttons
    document.getElementById(`del-btn-${id}`).style.display = "inline-block";
    document.getElementById(`edit-btn-${id}`).style.display = "inline-block";

    // Hide save/cancel buttons
    document.getElementById(`save-btn-${id}`).style.display = "none";
    document.getElementById(`cancel-btn-${id}`).style.display = "none";

    // Re-enable dropdown buttons
    var elements = document.getElementsByName('drop-btn');

    for (var i = 0; i < elements.length; i++){

        elements[i].disabled = false;
        
    }

}

// Edit input values in save for before post to backend
function saveEdit(id){

    // user inputs
    const row = document.getElementById(`row-${id}`)
    const edits = row.querySelectorAll("[id^='edit-']")
    
    // Form input fields (empty)
    const form = document.getElementById(`save-form-${id}`)

    // form value becomes user input values
    for (var i = 0; i < form.elements.length; i++){

        for (var j = 0; j < edits.length; j++){

            if (form.elements[i].name === edits[j].name){

                form.elements[i].value = edits[j].value;

                console.log(`Element ${i} \nform: ${form[i].name} - ${form[i].value} \nedits: ${edits[j].name} - ${edits[j].value}`)

                break;
            }
        }
    }
    return true;
}