/* landing page section starts here */

document.getElementById('dropArea').addEventListener('dragover', (event) => {
    event.stopPropagation();
    event.preventDefault();
    event.target.classList.add('hover');
}, false);

document.getElementById('dropArea').addEventListener('dragleave', (event) => {
    event.stopPropagation();
    event.preventDefault();
    event.target.classList.remove('hover');
}, false);

document.getElementById('dropArea').addEventListener('drop', (event) => {
    event.stopPropagation();
    event.preventDefault();
    const files = event.dataTransfer.files;
    document.getElementById('imageInput').files = files;
    event.target.classList.remove('hover');
}, false);

document.getElementById('imageInput').addEventListener('change', function() {
    drop_area = document.getElementById('dropArea')
    Array.from(this.files).forEach(file => {
        var new_div = document.createElement('div')
        var new_it = document.createElement('i')
        new_it.innerHTML = file.name + " " + (Math.round((file.size/1024/1024) * 100) / 100).toFixed(2) + "MB"
        new_div.appendChild(new_it)
        drop_area.appendChild(new_div)
    })
});

document.getElementById('dropArea').addEventListener('click', () => {
    document.getElementById('imageInput').click();
});

document.getElementById('addMusic').addEventListener('click', () => {
    document.getElementById('musicInput').click();
});

function handleFiles(files) {
    console.log(files);
    formdata = new FormData();
    files.forEach(file => {
        formdata.append(file.name,file)
    })
    fetch("http://localhost:5000/uploadImage",
        { method: "POST",
        headers:  {"x-access-token":window.localStorage.token},
        body: formdata
    }).then(r => r.json().then(data => ({status: r.status, body: data}))
    ).then(res => {
        console.log(res)
        alert(res.body.message)
        if (res.status==200) {
            window.location.replace('home.html')
        }

    })
}
function upload(){
    inp = document.getElementById('imageInput')
    files = Array.from(inp.files)
    handleFiles(files)
}

// Add additional functionalities as needed for customization and preview
function submitVideoOptions() {
    var select = document.getElementById("selectedImages")
    var result = [];
    var options = select && select.options;
    var opt;
    for (var i = 0, iLen = options.length; i < iLen; i++) {
        opt = options[i];

        if (opt.selected) {
            result.push(opt.value);
        }
    }
    var musicFile = Array.from(document.getElementById("musicInput").files)[0]
    var imgDuration = document.getElementById("imageDuration").value
    var formdata = new FormData()
    formdata.append(musicFile.name, musicFile)
    formdata.set("imgDuration", imgDuration)
    formdata.set("Image Ids", result)
    console.log(formdata)

    fetch("http://localhost:5000/setVideoOptions",
        { method: "POST",
        headers:  {"x-access-token":window.localStorage.token},
        body: formdata
    }).then(r => r.json().then(data => ({status: r.status, body: data}))
    ).then(res => {
        console.log(res)
        alert(res.body.message)
        if (res.status==200) {
            window.location.replace('createVideo.html')
        }

    })
}

/* landing page section ends here */


function selectPhotos() {
    fetch("http://localhost:5000/getMyImages",
        { method: "GET",
        headers:  {"x-access-token":window.localStorage.token}
        }).then(r => r.json().then(data => ({status: r.status, body: data}))
    ).then(res => {
        if (res.status==400) {
            alert(res.body.message)
            alert("Go to Image Upload")
        }
        if (res.status==200) {
            selImages = document.getElementById("selectedImages")
            Array.from(res.body['images']).forEach(img => {
                var new_option = document.createElement('option')
                new_option.value = img.id
                new_option.innerHTML = img.name
                selImages.appendChild(new_option)
            })
            console.log(res.body['images'])
        }

    })
}


/* video preview page starts here */


/* video preview page ends here */

/* login page starts here */
function redirect(){
    window.open('home.html');
}



function login() {
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    var loginmsg = document.getElementById("loginmsg");
    if (password=="" || email=="") {
        loginmsg.innerHTML = "Please fill both email and password"
        return
    }
    fetch("http://localhost:5000/login",
        { method: "POST",
        headers:  {"content-type":"application/json"},
        body: JSON.stringify({"email": email, "password": password})
    }).then(r => r.json().then(data => ({status: r.status, body: data}))
    ).then(res => {
        console.log(res)
        if (res.status!=200){
            loginmsg.innerHTML = res.body.message
        }
        else {
            localStorage.setItem('token', res.body['jwt-token'])
            window.location.replace("upload-images.html");
        }
    })
}

/* login page ends here */

/* signup page starts here */
function signup(){
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    var name = document.getElementById("name").value;
    var username = document.getElementById("username").value;
    var signupmsg = document.getElementById("signupmsg");
    if (password=="" || email=="" || name=="" || username=="") {
        signupmsg.innerHTML = "Please fill all the fields"
        return
    }
    payload = {"name": name, "username":username, "email":email,"password":password}
    headers = {"content-type":"application/json"}
    fetch("http://localhost:5000/signup",
        { method: "POST",
        headers: headers,
        body: JSON.stringify(payload)
    }).then(r => r.json().then(data => ({status: r.status, body: data}))
    ).then(res => {
        console.log(res)
        if (res.status != 200) {
            signupmsg.innerHTML = res.body.message
        }
        else {
            alert(res.body.message)
            window.location.replace("login.html");
        }

    })
}

/* signup page ends here */


function getMyVideoFrames() {
    fetch("http://localhost:5000/getVF",
        { method: "GET",
        headers:  {"x-access-token":window.localStorage.token}
        }).then(r => r.json().then(data => ({status: r.status, body: data}))
    ).then(res => {
        if (res.status==400) {
            alert(res.body.message)
            alert("Go to Video Options")
        }
        if (res.status===200) {
            let selImages = document.getElementById("images")
            let imgs  = Array.from(res.body['images'])
            let num_rows = Math.floor(imgs.length/3)
            if (num_rows===0) {
                num_rows=1
            }
            // console.log(num_rows)
            for (i=0; i<num_rows; i++){
                let new_tr = document.createElement('tr')
                for (j=0;j<3;j++){
                    // console.log(i,j)
                    let new_td = document.createElement('td')
                    let new_img = document.createElement('img')
                    new_img.src = imgs[i*3+j]['path']
                    new_td.appendChild(new_img)
                    new_tr.appendChild(new_td)
                }
                selImages.appendChild(new_tr)
            }
            // console.log(res.body['images'])
        }

    })
}



function getMyVideoPreview() {
    fetch("http://localhost:5000/createVid",
        { method: "GET",
        headers:  {"x-access-token":window.localStorage.token}
        }).then(r => r.json().then(data => ({status: r.status, body: data}))
    ).then(res => {
        if (res.status === 200) {
            let vidPreview = document.getElementById("videoPreview")
            vidPreview.src = res.body['path']
            let downloadButtons = document.getElementById("buttonDropdown")
            for (let i = 0; i < downloadButtons.children.length; i++) {
                let child = downloadButtons.children[i]
                child.href=res.body['res_paths'][i]
            }
            console.log(res.body)
        }
    })
}