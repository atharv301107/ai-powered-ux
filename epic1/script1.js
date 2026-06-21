function showForm(formId){

    document.querySelectorAll(".form").forEach(form=>{
        form.classList.remove("active");
    });

    document.getElementById(formId).classList.add("active");
}

function register(){

    let name=document.getElementById("name").value.trim();
    let email=document.getElementById("email").value.trim();
    let password=document.getElementById("password").value;
    let confirmPassword=document.getElementById("confirmPassword").value;

    let error=document.getElementById("registerError");

    error.innerHTML="";

    if(name===""){
        error.innerHTML="Name is required";
        return;
    }

    if(!email.includes("@")){
        error.innerHTML="Enter valid email";
        return;
    }

    if(password.length<8){
        error.innerHTML="Password must be at least 8 characters";
        return;
    }

    if(password!==confirmPassword){
        error.innerHTML="Passwords do not match";
        return;
    }

    alert("Registration Successful");
    showForm('loginForm');
}

function login(){

    let email=document.getElementById("loginEmail").value;
    let password=document.getElementById("loginPassword").value;

    if(email==="" || password===""){
        document.getElementById("loginError").innerHTML="All fields required";
        return;
    }

    alert("Login Successful");
}

function forgotPassword(){

    let email=document.getElementById("forgotEmail").value;

    if(email===""){
        document.getElementById("forgotError").innerHTML="Enter Email";
        return;
    }

    alert("Reset Link Sent Successfully");
}