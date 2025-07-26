document.addEventListener("DOMContentLoaded", function () {
  // Initialize countdown timer
  initCountdownTimer();

  // Initialize form handling
  initWaitlistForm();

  // Set dynamic year
  document.getElementById("year").textContent = new Date().getFullYear();

  // Add smooth scroll behavior for footer links
  initSmoothScroll();
});

function initCountdownTimer() {
  // Set target date (10 days from now for demo)
  const targetDate = new Date();
  targetDate.setDate(targetDate.getDate() + 10);
  targetDate.setHours(0, 0, 0, 0);

  const daysEl = document.getElementById("days");
  const hoursEl = document.getElementById("hours");
  const minutesEl = document.getElementById("minutes");
  const secondsEl = document.getElementById("seconds");

  function updateCountdown() {
    const now = new Date().getTime();
    const timeLeft = targetDate.getTime() - now;

    if (timeLeft > 0) {
      const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
      const hours = Math.floor(
        (timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
      );
      const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

      // Animate number changes
      animateNumberChange(daysEl, days);
      animateNumberChange(hoursEl, hours);
      animateNumberChange(minutesEl, minutes);
      animateNumberChange(secondsEl, seconds);
    } else {
      // Countdown finished
      daysEl.textContent = "00";
      hoursEl.textContent = "00";
      minutesEl.textContent = "00";
      secondsEl.textContent = "00";
    }
  }

  function animateNumberChange(element, newValue) {
    const currentValue = parseInt(element.textContent);
    const formattedValue = newValue.toString().padStart(2, "0");

    if (currentValue !== newValue) {
      element.style.transform = "scale(1.1)";
      element.style.color = "#fbbf24";

      setTimeout(() => {
        element.textContent = formattedValue;
        element.style.transform = "scale(1)";
        element.style.color = "white";
      }, 150);
    }
  }

  // Update countdown immediately and then every second
  updateCountdown();
  setInterval(updateCountdown, 1000);
}

function initWaitlistForm() {
  const form = document.querySelector(".waitlist-form");
  const emailInput = document.getElementById("email");
  const formMessage = document.querySelector(".form-message");
  const submitBtn = form.querySelector(".notify-btn");

  // Restore email from localStorage if present
  if (window.localStorage) {
    const savedEmail = localStorage.getItem("smartquery_waitlist_email");
    if (savedEmail) {
      emailInput.value = savedEmail;
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = emailInput.value.trim();

    if (!validateEmail(email)) {
      showMessage("Please enter a valid email address.", "error");
      return;
    }

    // Show loading state
    submitBtn.textContent = "Sending...";
    submitBtn.disabled = true;

    // Save to localStorage
    if (window.localStorage) {
      localStorage.setItem("smartquery_waitlist_email", email);
    }

    // Simulate API call
    setTimeout(() => {
      showMessage(
        "🎉 You're on the waitlist! We'll notify you when we launch.",
        "success"
      );

      // Disable form after success
      emailInput.disabled = true;
      submitBtn.textContent = "Subscribed!";
      submitBtn.style.background = "rgba(34, 197, 94, 0.3)";
      submitBtn.style.borderColor = "rgba(34, 197, 94, 0.5)";

      // Add success animation to the entire right side
      document.querySelector(".right-side").classList.add("success-pulse");
    }, 1500);
  });

  function showMessage(msg, type) {
    formMessage.textContent = msg;
    formMessage.className = "form-message " + type;
    formMessage.setAttribute("aria-live", "polite");
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  // Add input focus effects
  emailInput.addEventListener("focus", function () {
    this.parentElement.classList.add("focused");
  });

  emailInput.addEventListener("blur", function () {
    this.parentElement.classList.remove("focused");
  });
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
}

// Add some interactive hover effects
document.addEventListener("mousemove", function (e) {
  const rightSide = document.querySelector(".right-side");
  const rect = rightSide.getBoundingClientRect();

  if (
    e.clientX >= rect.left &&
    e.clientX <= rect.right &&
    e.clientY >= rect.top &&
    e.clientY <= rect.bottom
  ) {
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 20;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 20;

    rightSide.style.transform = `perspective(1000px) rotateY(${
      x * 0.1
    }deg) rotateX(${-y * 0.1}deg)`;
  } else {
    rightSide.style.transform =
      "perspective(1000px) rotateY(0deg) rotateX(0deg)";
  }
});

// Add CSS for success pulse animation
const style = document.createElement("style");
style.textContent = `
  .success-pulse {
    animation: success-pulse 2s ease-out;
  }
  
  @keyframes success-pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); box-shadow: 0 0 30px rgba(34, 197, 94, 0.3); }
    100% { transform: scale(1); }
  }
  
  .input-group.focused input {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
  }
`;
document.head.appendChild(style);
