const endTestBox = document.getElementById('endTestBox')
const endTestDate = Date.parse(endTestBox.textContent)
const timeLeft = document.getElementById('timeLeft')

const submitForm = document.getElementById('submit_form')

let leaveTime, joinTime

const student = document.getElementById('student').textContent

const startTestTime = new Date().getTime()

function sendLog(text){
    const fd = new FormData()

    fd.append('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value)
    fd.append('text', text)

    data = fd
    $.ajax({
        type: 'POST',
        url: 'send_test_log/',
        data: data,
        success: function (response){},
        error: function (response){},
        cache: false,
        contentType: false,
        processData: false,
    })
}


sendLog(`${new Date()} | ${student} rozpoczął/ęła sprawdzian`)

const countdown = setInterval(()=>{
    const now = new Date().getTime()
    const left = endTestDate - now

    const h = Math.floor((endTestDate / (1000*60*60) - (now / (1000*60*60)))%24)
    const m = Math.floor((endTestDate / (1000*60) - (now / (1000*60)))%60)
    const s = Math.floor((endTestDate / (1000) - (now / (1000)))%60)

    if (left > 0) {
        timeLeft.innerText ="Pozostało: " + h + " godzin, " + m  + " minut, "  + s  + " sekund"
    }else{
        clearInterval(countdown)
        submitForm.click()
    }
}, 1000)


window.addEventListener('blur', ()=>{

    let date = new Date()
    leaveTime = date.getTime()

    let h = Math.floor((leaveTime / (1000*60*60) - (startTestTime / (1000*60*60)))%24)
    let m = Math.floor((leaveTime / (1000*60) - (startTestTime / (1000*60)))%60)
    let s = Math.floor((leaveTime / (1000) - (startTestTime / (1000)))%60)

    if (s<10){
        s = `0${s}`
    }
    if (m<10){
        m = `0${m}`
    }

    sendLog(`Czas pisania sprawdzianu: ${h}:${m}:${s} | ${student} wyszedł ze sprawdzianu`)

    $.ajax({
        type: 'GET',
        url: 'student_left_test/',
        success: function (response){
            if (response.data.msg != '') {
                if (response.data.msg == 'end') {
                    submitForm.click()
                } else {
                    alert(response.data.msg);
                }
            }
        },
        error: function (response){

        },
    })
})


const stop = () =>{
    let date = new Date()
    joinTime = date.getTime()
    let dif = joinTime-leaveTime

    let m = Math.floor((dif / (1000*60))%60)
    let s = Math.floor((dif / (1000))%60)
    let ms = Math.floor(dif%1000)

    sendLog(`${student} powrócił do sprawdzianu po ${m} min, ${s} sek, ${ms} ms`)
}


window.addEventListener('focus', stop)


const colorInputs = document.getElementsByClassName('color')
const clearBtns = document.getElementsByClassName('clearBtn')
const canvases = document.getElementsByTagName('canvas')
const hiddenInputs = document.getElementsByClassName('hiddenInput')

Array.from(canvases).forEach((canvas)=>{
    canvas.width = window.innerWidth * 0.8
    canvas.height = window.innerHeight * 0.8
    const ctx = canvas.getContext('2d')
    let painting = false

    Array.from(colorInputs).forEach((color)=>{
        color.addEventListener('change', (e)=>{
            e.preventDefault()
            if (e.target.id == canvas.id){
                ctx.strokeStyle = `${e.target.value}`
            }
        })
    })

    Array.from(clearBtns).forEach((button)=>{
        button.addEventListener('click', (e)=>{
            e.preventDefault()
            if (e.target.id == canvas.id){
                ctx.clearRect(0,0,canvas.width, canvas.height)
            }
        })
    })

    Array.from(hiddenInputs).forEach((hidden)=>{
        canvas.addEventListener('mouseup', (e)=>{
            if (e.target.id == hidden.name){
                hidden.value = canvas.toDataURL()
            }
        })
    })

    function startPositioning(e){
        painting = true
        draw(e)
    }

    function finishedPosition(){
        painting = false
        ctx.beginPath()
    }

    function draw(e){
        if (!painting) return
        ctx.lineWidth = 3
        ctx.lineCap = 'round'

        ctx.lineTo(e.layerX, e.layerY)
        ctx.stroke()
        ctx.beginPath()
        ctx.moveTo(e.layerX, e.layerY)
    }

    window.addEventListener('resize', ()=>{
        canvas.width = window.innerWidth * 0.8
        canvas.height = window.innerHeight * 0.8
    })

    canvas.addEventListener("mousedown", startPositioning)
    canvas.addEventListener("mouseup", finishedPosition)
    canvas.addEventListener("mousemove", draw)
    canvas.addEventListener("mouseout", finishedPosition)
})


document.addEventListener('contextmenu', (e)=>{
    e.preventDefault()
})


const testForm = document.getElementById('testForm')

testForm.addEventListener('submit', ()=>{
    sendLog(`${new Date()} | ${student} zakończył/a sprawdzian`)
})