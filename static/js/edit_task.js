const typeOfTask = document.getElementById('type_of_task')
const csrf = document.getElementsByName('csrfmiddlewaretoken')
const task_id = document.getElementById('task_id')

if (typeOfTask.textContent == 'zamkniete'){
    const answerOptions = document.getElementById('answer_options')
    const addAnswerOptionForm = document.getElementById('addAnswerOptionForm')
    const ansOptText = document.getElementById('ans_option_text')
    const ansOptImg = document.getElementById('ans_option_image')
    const ansOptIsCorrect = document.getElementById('ans_option_is_correct')
    const get_answer_options = () =>{
        $.ajax({
            type: 'GET',
            url: 'get-answer-options/',
            success: function (response){
                answerOptions.innerHTML = ''
                response.qs.forEach((item)=>{
                    const li = document.createElement('li')
                    const br = document.createElement('br')
                    const br2 = document.createElement('br')
                    const br3 = document.createElement('br')
                    const labelText = document.createElement('label')
                    labelText.textContent = 'Tekst: '
                    const text = document.createElement('input')
                    text.setAttribute('name', `${item.id}_label`)
                    text.setAttribute('value', item.label)
                    text.setAttribute('type', 'text')
                    const img = document.createElement('img')
                    if (item.img) {
                        img.src = `${window.location.protocol}//${window.location.host}/media/${item.img}`
                    }
                    const labelImg = document.createElement('label')
                    const deleteImg = document.createElement('a')
                    if (item.img){
                        labelImg.textContent = 'Zmień zdjęcie'
                        deleteImg.setAttribute('href', `ans-opt/${item.id}/delete-img/`)
                        deleteImg.textContent = 'Usuń zdjęcie'
                    }else{
                        labelImg.textContent = 'Dodaj zdjęcie'
                    }
                    const inputImg = document.createElement('input')
                    inputImg.setAttribute('type', 'file')
                    inputImg.setAttribute('name', `${item.id}_image`)
                    inputImg.setAttribute('accept', 'image/*')
                    const labelIsCorrect = document.createElement('label')
                    labelIsCorrect.textContent = 'Czy to poprawna odpowiedz?'
                    const isCorrect = document.createElement('input')
                    isCorrect.setAttribute('type', 'checkbox')
                    isCorrect.setAttribute('name', `${item.id}_is_correct`)
                    isCorrect.setAttribute('class', 'is_correct')
                    if (item.is_correct){
                        isCorrect.checked = true
                    }else{
                        isCorrect.checked = false
                    }
                    const a = document.createElement('a')
                    a.textContent = 'Usuń'
                    a.setAttribute('href', window.location.href + `delete_answer_option/${item.id}/`)
                    li.appendChild(labelText)
                    li.appendChild(text)
                    li.appendChild(img)
                    li.appendChild(br)
                    li.appendChild(labelImg)
                    li.appendChild(inputImg)
                    li.appendChild(deleteImg)
                    li.appendChild(br2)
                    li.appendChild(labelIsCorrect)
                    li.appendChild(isCorrect)
                    li.appendChild(document.createElement('br'))
                    li.appendChild(a)
                    answerOptions.appendChild(li)
                    answerOptions.appendChild(br3)
                })

            }
        })
    }
    get_answer_options()


    addAnswerOptionForm.addEventListener('submit', (e)=>{
    e.preventDefault()
    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('task_id', task_id.innerText)
    fd.append('text', ansOptText.value)
    fd.append('img', ansOptImg.files[0])


    if (ansOptIsCorrect.checked){
        fd.append('is_correct', '1')
    }else {
        fd.append('is_correct', '0')
    }

    $.ajax({
        type: 'POST',
        url: window.location.href + 'add_answer_option/',
        enctype: 'multipart/form-data',
        data: fd,
        success: function (response){
            get_answer_options()
            addAnswerOptionForm.reset()
        },
        error: function (response){

        },
        cache: false,
        contentType: false,
        processData: false,
    })
})
}


if (typeOfTask.textContent == 'prawda/fałsz'){
    const trueFalseSentences = document.getElementById('trueFalseSentences')
    const pointsTask = document.getElementById('points')

    const addTrueFalseTaskForm = document.getElementById('addTrueFalseTaskForm')
    const trueFalseContent = document.getElementById('trueFalseContent')
    const isTrue = document.getElementById('true')
    const pointsTF = document.getElementById('pointsTF')
    const pointsFields = document.getElementsByClassName('pointsTF')

    pointsTask.addEventListener('change', (e)=>{
        if (e.target.value != '0'){
            Array.from(pointsFields).forEach((item)=>{
                item.disabled = true
                item.value = 0
            })
            pointsTF.disabled = true
            pointsTF.value = 0
        }else{
            Array.from(pointsFields).forEach((item)=>{
            item.disabled = false
            })
            pointsTF.disabled = false
        }
    })

    if (pointsTask.value != '0'){
        Array.from(pointsFields).forEach((item)=>{
            item.disabled = true
            item.value = 0
        })
        pointsTF.disabled = true
        pointsTF.value = 0
    }else{
        Array.from(pointsFields).forEach((item)=>{
        item.disabled = false
        })
        pointsTF.disabled = false
    }

    const get_true_false_sentences = ()=>{
        $.ajax({
            type: 'GET',
            url: 'get-true-false-sentences/',
            success: function (response){
                trueFalseSentences.innerHTML = ''
                response.qs.forEach((item)=>{
                    const li = document.createElement('li')
                    const br = document.createElement('br')
                    const textLabel = document.createElement('label')
                    textLabel.textContent = 'Tekst:'
                    const inputText = document.createElement('input')
                    inputText.setAttribute('value', item.content)
                    inputText.setAttribute('type', 'text')
                    inputText.setAttribute('name', `${item.id}_content`)
                    const isTrue = document.createElement('input')
                    isTrue.setAttribute('type', 'radio')
                    isTrue.setAttribute('name', `${item.id}_is_correct`)
                    isTrue.setAttribute('value', 'true')
                    const isTrueLabel = document.createElement('label')
                    isTrueLabel.textContent = 'Prawda'
                    const isFalseLabel = document.createElement('label')
                    isFalseLabel.textContent = 'Fałsz'
                    const isFalse = document.createElement('input')
                    isFalse.setAttribute('type', 'radio')
                    isFalse.setAttribute('name', `${item.id}_is_correct`)
                    isFalse.setAttribute('value', 'false')
                     if (item.is_correct){
                        isTrue.checked = true
                    }else{
                        isFalse.checked = true
                    }
                    const pointsLabel = document.createElement('label')
                    pointsLabel.textContent = 'Podaj liczbę punktów:'
                    const info = document.createElement('p')
                    info.textContent = "Pozostaw 0 gdy chcesz by zadanie było oceniane jako całość"
                    const points = document.createElement('input')
                    points.setAttribute('value', item.points)
                    points.setAttribute('type', 'number')
                    points.setAttribute('class', 'pointsTF')
                    points.setAttribute('name', `${item.id}_points`)
                    if (pointsTask.value != '0'){
                        points.setAttribute('value', 0)
                        points.disabled = true
                    }
                    const a = document.createElement('a')
                    a.setAttribute('href', window.location.href + `delete-true-false-sentence/${item.id}/`)
                    a.textContent = 'Usuń'
                    li.appendChild(textLabel)
                    li.appendChild(inputText)
                    li.appendChild(isTrue)
                    li.appendChild(isTrueLabel)
                    li.appendChild(isFalse)
                    li.appendChild(isFalseLabel)
                    li.appendChild(br)
                    li.appendChild(pointsLabel)
                    li.appendChild(info)
                    li.appendChild(points)
                    li.appendChild(document.createElement('br'))
                    li.appendChild(a)
                    trueFalseSentences.appendChild(li)
                    trueFalseSentences.appendChild(document.createElement('br'))
                })
            },
            error: function (response){

            }
        })
    }

    get_true_false_sentences()


    addTrueFalseTaskForm.addEventListener('submit', (e)=>{
        e.preventDefault()
        const fd = new FormData()
        fd.append('csrfmiddlewaretoken', csrf[0].value)
        fd.append('content', trueFalseContent.value)
        if (isTrue.checked){
            fd.append('is_correct', 'true')
        }else{
            fd.append('is_correct', 'false')
        }
        fd.append('points', pointsTF.value)

        $.ajax({
            type: 'POST',
            url: "add-true-false-sentence/",
            data: fd,
            success: function (response){
                get_true_false_sentences()
                addTrueFalseTaskForm.reset()
            },
            error: function (response){

            },
            cache: false,
            contentType: false,
            processData: false,
        })
    })
}