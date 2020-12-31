const are_exits_allowed = document.getElementById('are_exits_allowed')
const allowed_exits_box = document.getElementById('allowed_exits_box')

are_exits_allowed.addEventListener('change', ()=> {
    if (are_exits_allowed.checked){
        allowed_exits_box.hidden = false
    }else{
        allowed_exits_box.hidden = true
    }
})