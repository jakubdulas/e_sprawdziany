const schedule_elements = document.getElementById('schedule_elements')
const input = document.getElementById('date')
const group = document.getElementsByName('group')[0].value

input.addEventListener('change', ()=>{
    const date = new Date(input.value)
    let day = date.getDay()

    if (day == 0){
        day = 6
    }else{
        day -= 1
    }

    $.ajax({
        url: `${window.location.origin}/school/get_schedule_elements/${group}/${day}/`,
        type: 'GET',
        success: function (response){
            schedule_elements.innerHTML = ''
            response.schedule_elements.forEach(element =>{
                const option = document.createElement('option')
                option.value = element.id
                option.textContent = `${element.bell__number_of_lesson}`
                schedule_elements.appendChild(option)
            })
        },
        error: function (response){

        }
    })
})