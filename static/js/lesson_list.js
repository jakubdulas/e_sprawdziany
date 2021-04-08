const next_week_btn = document.getElementById('next-week')
const prev_week_btn = document.getElementById('prev-week')
const week_text = document.getElementById('week')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

let date = new Date()


const send_week = ()=>{
    let week = []
    let curr = new Date(date.getTime())

    for (let i = 1; i <= 5; i++) {
        let first = curr.getDate() - curr.getDay() + i
        let day = new Date(curr.setDate(first)).toISOString().slice(0, 10)
        week.push(day)
    }

    let first_day = week[0]
    let last_day = week[4]

    week_text.textContent = `${first_day} - ${last_day}`

    const fd = new FormData()
    fd.append('start', first_day)
    fd.append('end', last_day)
    fd.append('csrfmiddlewaretoken', csrf[0].value)

    $.ajax({
        url: '',
        type: 'POST',
        data: fd,
        success: function (response){
            for (let i = 0; i < response.number_of_lessons; i++){
                let mon = response.mon[i]
                document.getElementById(`0-${i}`).innerHTML = ''
                if (mon != null){
                    let el = document.createElement('a')
                    el.href = `${window.location.origin}/school/start-lesson/${mon.schedule_element}/${mon.year}/${mon.month}/${mon.day}/`
                    el.textContent = `${mon.group}`
                    document.getElementById(`${mon.day_of_week}-${mon.number_of_lesson}`).appendChild(el)
                }

                let tues = response.tues[i]
                document.getElementById(`1-${i}`).innerHTML = ''
                if (tues != null){
                    let el = document.createElement('a')
                    el.href = `${window.location.origin}/school/start-lesson/${tues.schedule_element}/${tues.year}/${tues.month}/${tues.day}/`
                    el.textContent = `${tues.group}`
                    document.getElementById(`${tues.day_of_week}-${tues.number_of_lesson}`).appendChild(el)
                }

                let wed = response.wed[i]
                document.getElementById(`2-${i}`).innerHTML = ''
                if (wed != null){
                    let el = document.createElement('a')
                    el.href = `${window.location.origin}/school/start-lesson/${wed.schedule_element}/${wed.year}/${wed.month}/${wed.day}/`
                    el.textContent = `${wed.group}`
                    document.getElementById(`${wed.day_of_week}-${wed.number_of_lesson}`).appendChild(el)
                }

                let thur = response.thur[i]
                document.getElementById(`3-${i}`).innerHTML = ''
                if (thur != null){
                    let el = document.createElement('a')
                    el.href = `${window.location.origin}/school/start-lesson/${thur.schedule_element}/${thur.year}/${thur.month}/${thur.day}/`
                    el.textContent = `${thur.group}`
                    document.getElementById(`${thur.day_of_week}-${thur.number_of_lesson}`).appendChild(el)
                }

                let fri = response.fri[i]
                document.getElementById(`4-${i}`).innerHTML = ''
                if (fri != null){
                    let el = document.createElement('a')
                    el.href = `${window.location.origin}/school/start-lesson/${fri.schedule_element}/${fri.year}/${fri.month}/${fri.day}/`
                    el.textContent = `${fri.group}`
                    document.getElementById(`${fri.day_of_week}-${fri.number_of_lesson}`).appendChild(el)
                }
            }

        },
        error: function (response){

        },
        cache: false,
        contentType: false,
        processData: false,
    })
}

send_week()

prev_week_btn.addEventListener('click', (e)=>{
    e.preventDefault()
    let pastDate = date.getDate() - 7;
    date.setDate(pastDate);
    send_week()
})

next_week_btn.addEventListener('click', (e)=>{
    e.preventDefault()
    let futureDate = date.getDate() + 7;
    date.setDate(futureDate);
    send_week()
})