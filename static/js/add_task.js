const type_of_task_dropdown = document.getElementById('type_od_task_dropdown')
const add_task_form = document.getElementById('add_task_form')
const content = document.getElementById('content')
const points = document.getElementById('points')
const image = document.getElementById('image')
const imgBox = document.getElementById('imageBox')
const btn = document.getElementById('add_task_btn')
const csrf = document.getElementsByName('csrfmiddlewaretoken')
const form = document.getElementById('form')
const task_id = document.getElementById('task_id')
const file = document.getElementById('file')

const info = document.getElementById('info')
const addAnswerOptionForm = document.getElementById('addAnswerOptionForm')
const addAnswerOptionText = document.getElementById('ans_option_text')
const addAnswerOptionBtn = document.getElementById('ans_option_button')
const addAnswerOptionIsCorrect = document.getElementById('ans_option_is_correct')
const answerOptions = document.getElementById('answer_options')
const addAnswerOptionImage = document.getElementById('ans_option_image')

const addCorrectAnswerForm = document.getElementById('addCorrectAnswer')
const info2 = document.getElementById('info-2')
const addCorrectAnswerText = document.getElementById('correct_answer_text')
const correctAnswer = document.getElementById('correct_answer')
const addCorrectAnswerBtn = document.getElementById('add_correct_answer_btn')


const addTrueFalseTaskFrom = document.getElementById('addTrueFalseTask')
const trueFalseContent = document.getElementById('trueFalseContent')
const isTrue = document.getElementById('true')
const isFalse = document.getElementById('false')
const pointsTF = document.getElementById('pointsTF')
const tfOptions = document.getElementById('true_false_options')
const addTrueFalseTaskBtn = document.getElementById('add_true_false_option_btn')
const info3 = document.getElementById('info3')
const info4 = document.getElementById('info4')

add_task_form.addEventListener('submit', (e)=>{
    e.preventDefault()
    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('type', type_of_task_dropdown.value)
    fd.append('content', content.value)
    fd.append('points', points.value)
    fd.append('image', image.files[0])
    fd.append('file', file.files[0])
    $.ajax({
        type: 'POST',
        url: window.location.href,
        enctype: 'multipart/form-data',
        data: fd,
        success: function (response){
            type_of_task_dropdown.disabled = true
            image.disabled = true
            points.disabled = true
            content.disabled = true
            task_id.innerText = response.data.task_id
            btn.disabled = true
            file.disabled = true

            addAnswerOptionBtn.disabled = false
            addAnswerOptionIsCorrect.disabled = false
            addAnswerOptionText.disabled = false
            addAnswerOptionImage.disabled = false

            addCorrectAnswerBtn.disabled = false
            addCorrectAnswerText.disabled = false

            trueFalseContent.disabled = false
            isTrue.disabled = false
            isFalse.disabled = false

            if (points.value == '0') {
                pointsTF.disabled = false
            }

            addTrueFalseTaskBtn.disabled = false

            info.innerText = ''
            info2.innerText = ''

        },
        error: function (response){
            add_task_form.reset()
        },
        cache: false,
        contentType: false,
        processData: false,
    })
})


image.addEventListener('change', ()=>{
    const imgData = image.files[0]
    const url = URL.createObjectURL(imgData)
    imgBox.setAttribute('src', url)
})


$.ajax({
    type: 'GET',
    url: 'get-types-of-tasks/',
    success: function (response){
        const typesData = response.data
        typesData.map(type=>{
            const option = document.createElement('option')
            option.textContent = type.label
            option.setAttribute('value', type.id)
            type_of_task_dropdown.appendChild(option)
        })
    },
    error: function (response){

    },
})

type_of_task_dropdown.addEventListener('change', (e)=>{
    const selectedType = e.target.value
    switch (selectedType){
        case '1':
            addAnswerOptionForm.hidden = false
            addCorrectAnswerForm.hidden = true
            addTrueFalseTaskFrom.hidden = true

            info3.hidden = true
            info4.hidden = true
            break
        case '2':
            addAnswerOptionForm.hidden = true
            addCorrectAnswerForm.hidden = true
            addTrueFalseTaskFrom.hidden = true

            info3.hidden = true
            info4.hidden = true
            break
        case '3':
            addAnswerOptionForm.hidden = true
            addCorrectAnswerForm.hidden = true
            addTrueFalseTaskFrom.hidden = true

            info3.hidden = true
            info4.hidden = true
            break
        case '4':
            addAnswerOptionForm.hidden = true
            addCorrectAnswerForm.hidden = false
            addTrueFalseTaskFrom.hidden = true

            info3.hidden = true
            info4.hidden = true
            break
        case '5':
            addTrueFalseTaskFrom.hidden = false
            addCorrectAnswerForm.hidden = true
            addAnswerOptionForm.hidden =  true

            info3.hidden = false
            info4.hidden = false
            break
    }
})


addAnswerOptionForm.addEventListener('submit', (e)=>{
    e.preventDefault()
    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('task_id', task_id.innerText)
    fd.append('text', addAnswerOptionText.value)
    fd.append('img', addAnswerOptionImage.files[0])


    if (addAnswerOptionIsCorrect.checked){
        fd.append('is_correct', '1')
    }else {
        fd.append('is_correct', '0')
    }

    $.ajax({
        type: 'POST',
        url: window.location.href + 'answer-option/',
        enctype: 'multipart/form-data',
        data: fd,
        success: function (response){
            answerOptions.hidden = false

            const option = document.createElement('li')
            option.textContent = response.ansOptionLabel
            answerOptions.appendChild(option)

            if (response.imgUrl){
                const img = document.createElement('img')
                img.src = response.imgUrl
                answerOptions.appendChild(img)
            }


            addAnswerOptionForm.reset()
        },
        error: function (response){

        },
        cache: false,
        contentType: false,
        processData: false,
    })
})


addCorrectAnswerForm.addEventListener('submit', (e)=>{
    e.preventDefault()
    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('task_id', task_id.innerText)
    fd.append('correct_answer', addCorrectAnswerText.value)

    $.ajax({
        type: 'POST',
        url: window.location.href + 'correct-answer/',
        data: fd,
        success: function (response){
            correctAnswer.hidden = false
            correctAnswer.textContent = response.correct_answer
            addCorrectAnswerForm.hidden = true
        },
        error: function (response){

        },
        cache: false,
        contentType: false,
        processData: false,
    })
})


addTrueFalseTaskFrom.addEventListener('submit', (e)=>{
    e.preventDefault()
    const fd = new FormData()
    fd.append('content', trueFalseContent.value)
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    if (isTrue.checked){
        fd.append('isTrue', '1')
    }else{
        fd.append('isTrue', '0')
    }
    fd.append('task_id', task_id.textContent)
    fd.append('points', pointsTF.value)

    $.ajax({
        url: 'truefalse-option/',
        type: 'POST',
        data: fd,
        success: function (response){
            tfOptions.hidden = false

            const option = document.createElement('li')
            option.textContent = `${response.content}: ${response.is_correct}`
            tfOptions.appendChild(option)

            addTrueFalseTaskFrom.reset()
        },
        error: function (response){

        },
        cache: false,
        contentType: false,
        processData: false,
    })
})