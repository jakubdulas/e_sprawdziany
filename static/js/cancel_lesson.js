school_class = document.getElementById('school_class')
group_select = document.getElementById('group')

school_class.addEventListener('change', (e)=>{
    chosen_item = e.target.value
    if (chosen_item == -1){
        return
    }
    $.ajax({
        url: `get_groups/${chosen_item}/`,
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