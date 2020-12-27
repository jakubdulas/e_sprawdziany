const endTestBox = document.getElementById('endTestBox')
const endTestDate = Date.parse(endTestBox.textContent)
const timeLeft = document.getElementById('timeLeft')

const submitForm = document.getElementById('submit_form')

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