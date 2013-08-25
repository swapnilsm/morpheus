function loadFile() {
    $("#myModal").modal();

    // Retrieve the FileList object from the referenced element ID
    var myFileList = document.getElementById('upload_file').files;
    var time = parseInt(document.getElementById('time').value);
 
    // Grab the first File Object from the FileList
    var myFile = myFileList[0];
 
    // Set some variables containing the three attributes of the file
    var myFileName = myFile.name;
    var myFileSize = myFile.size;
    var myFileType = myFile.type;
 
    // Let's upload the complete file object
    uploadFile(myFile, time);
}

function passUrl() {
    $("#myModal").modal();
    var url = document.getElementById('url').value;
    var time = parseInt(document.getElementById('time').value);
    uploadFile('', time, url)
}

function uploadFile(myFileObject, time, url) {
    // Open Our formData Object
    var formData = new FormData();
 
    // Append our file to the formData object
    // Notice the first argument "file" and keep it in mind
    if (url)
	formData.append('url', url);
    else
	formData.append('file', myFileObject);

 
    // Create our XMLHttpRequest Object
    var xhr = new XMLHttpRequest();
 
    // Open our connection using the POST method
    if (time) 
        xhr.open("POST", '/uploader.php?t='+time);
    else
        xhr.open("POST", '/uploader.php');

    xhr.onload = function () {
        if (xhr.status === 200) {
            redirect(xhr.responseText)
        } else {
            alert("Something went wrong!!!")
        }
    };

    
    
    // Send the file
    xhr.send(formData);
}

function redirect(filename) {
    window.location.href="view.html?f="+filename
}

function getURLParameter(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}

