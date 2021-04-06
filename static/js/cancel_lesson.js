const school_class = document.getElementById('school_class')
const group_select = document.getElementById('group')
const number_of_lesson = document.getElementById('number_of_lesson')
const date_field = document.getElementById('date')
let date
let day

date_field.addEventListener('change', (e)=>{
    date = new Date(e.target.value)
    day = date.getDay()

    if (day == 0){
        day = 6
    }else{
        day -= 1
    }
})

school_class.addEventListener('change', (e)=>{
    if (!day && !number_of_lesson){
        group_select.disabled = true
        return;
    }
    group_select.disabled = false

    chosen_item = e.target.value
    if (chosen_item == -1){
        return
    }
    $.ajax({
        url: `get_groups/${chosen_item}/${number_of_lesson.value}/${day}`,
        type: 'GET',
        success: function (response){
            group_select.innerHTML = ""
            const first_option = document.createElement('option')
            first_option.textContent = "------"
            first_option.value = -1
            group_select.appendChild(first_option)
            response.groups.map(group=>{
                const option = document.createElement('option')
                option.textContent = group.name
                option.value = group.id
                group_select.appendChild(option)
            })
        },
        error: function (response){

        }
    })
})