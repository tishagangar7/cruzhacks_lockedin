const API_BASE_URL = "http://127.0.0.1:5000";

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const messageEl = document.getElementById("login-message");

  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (data.success) {
      localStorage.setItem("user_id", data.user_id);
      window.location.href = "dashboard.html";
    } else {
      messageEl.textContent = data.message || "Login failed.";
    }
  } catch (error) {
    console.error("Error during login:", error);
    messageEl.textContent = "An error occurred. Try again.";
  }
});
