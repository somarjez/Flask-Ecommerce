// Select elements
const loginText = document.querySelector(".title-text .login");
const signupText = document.querySelector(".title-text .signup");
const loginForm = document.querySelector("form.login");
const signupForm = document.querySelector("form.signup");
const loginBtn = document.querySelector("label.login");
const signupBtn = document.querySelector("label.signup");
const signupLink = document.querySelector("form.login .signup a");
const formInner = document.querySelector(".form-inner");

// Function to switch to signup
signupBtn.onclick = () => {
    formInner.style.transform = "translateX(-100%)"; // Slide left for signup
    loginText.style.display = "none"; // Hide login text
    signupText.style.display = "block"; // Show signup text
};

// Function to switch to login
loginBtn.onclick = () => {
    formInner.style.transform = "translateX(0%)"; // Slide right for login
    loginText.style.display = "block"; // Show login text
    signupText.style.display = "none"; // Hide signup text
};

// Update the signupLink to switch to signup form
signupLink.onclick = (event) => {
    event.preventDefault(); // Prevent the default anchor behavior
    signupBtn.click(); // Simulate the signup button click
};

document.addEventListener("DOMContentLoaded", function() {
    const elements = document.querySelectorAll('.fade-in, .slide-in');

    // Trigger animations on page load
    elements.forEach((element) => {
        element.classList.add('fade-in');
    });

    // Example of fade out effect after a certain duration
    setTimeout(() => {
        elements.forEach((element) => {
            element.classList.remove('fade-in');
            element.classList.add('fade-out');
            // Optionally remove the element after fading out
            element.classList.add('hidden');
        });
    }, 5000); // Adjust time as necessary (5000 ms = 5 seconds)
});


