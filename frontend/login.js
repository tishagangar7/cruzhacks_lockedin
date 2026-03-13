const API_BASE_URL = window.location.origin;

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const remember = document.querySelector('input[name="remember"]')?.checked ?? true;
  const messageEl = document.getElementById("login-message");

  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password, remember }),
    });

    const data = await response.json();

    if (data.success) {
      // Store user_id in localStorage
      localStorage.setItem("user_id", data.user_id);

      // Redirect to index.html
      window.location.href = "index.html";
    } else {
      // Display error message
      messageEl.textContent = data.message || "Login failed. Please try again.";
      messageEl.style.color = "red";
    }
  } catch (error) {
    console.error("Error during login:", error);
    messageEl.textContent = "An error occurred. Please try again.";
    messageEl.style.color = "red";
  }
});