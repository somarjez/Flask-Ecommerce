function signup() {
    const loginForm = document.querySelector(".login-form-container");
    const signupForm = document.querySelector(".signup-form-container");
    const container = document.querySelector(".container");

    // Hide login form
    loginForm.classList.remove("show");
    setTimeout(() => {
        loginForm.style.display = "none"; // Hide after animation
        // Show signup form
        signupForm.style.display = "block";
        setTimeout(() => {
            signupForm.classList.add("show");
        }, 10); // Delay to allow for the display to update
    }, 500); // Animation duration
    container.style.background = "linear-gradient(to bottom, rgb(56, 189, 149), rgb(28, 139, 106))";
    document.querySelector(".button-1").style.display = "none"; // Hide the login button
    document.querySelector(".button-2").style.display = "block"; // Show the signup button
}

function login() {
    const loginForm = document.querySelector(".login-form-container");
    const signupForm = document.querySelector(".signup-form-container");
    const container = document.querySelector(".container");

    // Hide signup form
    signupForm.classList.remove("show");
    setTimeout(() => {
        signupForm.style.display = "none"; // Hide after animation
        // Show login form
        loginForm.style.display = "block";
        setTimeout(() => {
            loginForm.classList.add("show");
        }, 10); // Delay to allow for the display to update
    }, 500); // Animation duration
    container.style.background = "linear-gradient(to bottom, rgb(6, 108, 224), rgb(14, 48, 122))";
    document.querySelector(".button-2").style.display = "none"; // Hide the signup button
    document.querySelector(".button-1").style.display = "block"; // Show the login button
}
