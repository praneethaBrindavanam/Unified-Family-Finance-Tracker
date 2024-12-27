document.querySelector("form").addEventListener("submit", async (e) => {
    e.preventDefault(); // Prevent form from refreshing the page
  
    const email = document.querySelector("input[type='email']").value;
  
    try {
      const response = await fetch("http://127.0.0.1:5000/send-reset-link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
  
      const result = await response.json();
      if (response.ok) {
        alert(result.message); // Success message
      } else {
        alert(result.message); // Error message from backend
      }
    } catch (error) {
      alert("Something went wrong. Please try again.");
    }
  });
  