const recipients = document.getElementsByName('recipient')
const recipientsBox = document.getElementById('recipientsBox')

recipients.forEach((item)=>{
    item.addEventListener('change', (e)=>{
        switch (e.target.value){
            case 'teachers':

                break
            case 'student':
                break
        }
    })
})