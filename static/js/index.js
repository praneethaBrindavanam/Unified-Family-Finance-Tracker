function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
  }

  // Slideshow Script
  let slideIndex = 0;
  function showSlides() {
    let slides = document.getElementsByClassName("mySlides");
    for (let i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) { slideIndex = 1 }
    slides[slideIndex - 1].style.display = "block";
    setTimeout(showSlides, 2000); // Change image every 2 seconds
  }

  // Modal Script
  function closeModal() {
    document.getElementById("myModal").style.display = "none";
  }
  
  window.onload = showSlides;

async function resolveAlert(id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/MarkAlert', {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ "alert_id": id })
    });

    if (!response.ok) {
      throw new Error("Failed to Mark Alert. Status: " + response.status);
    }
    
    // Remove or update the alert in the UI
    const alertElement = document.getElementById(`alert-${id}`);
    if (alertElement) {
      alertElement.remove(); // Remove alert from the DOM
    }
  } catch (error) {
    console.error("Error Updating Alert Status:", error);
  }
}

async function displayAlerts() {
  const container = document.getElementById("alert-container");

  // Avoid loading duplicate alerts
  if (container.childElementCount > 0) return;

  try {
    const response = await fetch("http://127.0.0.1:5000/Alerts", {
      method: "GET",
    });
    const alerts = await response.json();
    console.log(alerts["alerts"]);

    for (const alert of alerts["alerts"]) {
      document.getElementById("blankmessage").style.display = "none";

      // Create alert element
      const node = document.createElement("div");
      node.id = `alert-${alert[0]}`; // Unique ID for the alert
      node.innerHTML = `
        <div class="alert ${alert[3] === 'Warning' ? 'alert-primary' : 'alert-danger'}" role="alert">
          <div class="hstack gap-3">
            <div class="p-0">BudgetId-${alert[4]}</div>
            <div class="p-0">${alert[1]}</div>
            <div class="p-0">
              <a class="btn" data-bs-toggle="collapse" href="#details-${alert[0]}" role="button" aria-expanded="false" aria-controls="collapseExample">
                🔽
              </a>
            </div>
          </div>
          <div class="collapse" id="details-${alert[0]}">
            <div class="card card-body">
              <p>${alert[2]}</p>
              <button onclick="resolveAlert(${alert[0]})" class="btn btn-success">
                <i class="fas fa-check-circle"></i> Mark As Resolved
              </button>
            </div>
          </div>              
        </div>`;
      
      container.appendChild(node);
    }
  } catch (error) {
    console.error("Error fetching alerts:", error);
  }
}


async function getPercentage() {
  try {
      const response = await fetch('http://127.0.0.1:5000/BudgetPercentage', {
          method: "GET",
      });
      if (!response.ok) {
          throw new Error("Failed to fetch percentage. Status: " + response.status);
      }
      const data = await response.json();
      console.log("Raw data received:", data);

      const percentage = data["percent"];
      
      // Validate and clamp percentage
      if (isNaN(percentage)) {
          throw new Error("Invalid percentage value received: " + percentage);
      }
      const validPercentage = Math.min(Math.max(percentage, 0), 100);

      // Update progress bar
      const bar = document.getElementById("budgetpercentage");
      if (!bar) {
          throw new Error("Progress bar element not found in DOM.");
      }
      bar.style.width = validPercentage + "%";
      bar.innerText = `${validPercentage.toFixed(2)}% limit exhausted`;
      bar.setAttribute("aria-valuenow", validPercentage);
  } catch (error) {
      console.error("Error fetching budget percentage:", error);

      // Handle missing or error state in the UI
      const bar = document.getElementById("budgetpercentage");
      if (bar) {
          bar.style.width = "0%";
          bar.innerText = "Error loading budget data";
      }
  }
}


async function resolveAlert(id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/MarkAlert', {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ "alert_id": id })
    });

    if (!response.ok) {
      throw new Error("Failed to Mark Alert. Status: " + response.status);
    }
    
    const alertElement = document.getElementById(`alert-${id}`);
    if (alertElement) {
      alertElement.remove(); 
    }
  } catch (error) {
    console.error("Error Updating Alert Status:", error);
  }
}


document.addEventListener("DOMContentLoaded", function() {
  getPercentage();
});
