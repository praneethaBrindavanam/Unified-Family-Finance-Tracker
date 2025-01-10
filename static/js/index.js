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

async function displayAlerts(){
  const container=document.getElementById("alert-container")
  if(container.childElementCount>0) return;
  response=await fetch("http://127.0.0.1:5000/Alerts",{
    method:"GET"
  })
  alerts=await response.json()
  console.log(alerts["alerts"]);
  for(alert of alerts["alerts"]){
    const node=document.createElement("div")
    node.innerHTML=`<div class="alert ${alert[3]=='Warning'?'alert-primary':'alert-danger'}" role="alert">
                      <div class="hstack gap-3">
                      <div class="p-0">BudgetId-${alert[4]}</div>
                      <div class="p-0">${alert[1]}</div>
                      <div class="p-0">
                        <a class="btn" data-bs-toggle="collapse" href="#${alert[0]}" role="button" aria-expanded="false" aria-controls="collapseExample">
                        🔽
                        </a>
                      </div>
                      </div>
              <div class="collapse" id="${alert[0]}">
                <div class="card card-body">
                  <p>${alert[2]}</p>
                </div>
              </div>              
          </div>`
    container.appendChild(node);
  }
}

async function getPercentage() {
  try {
      const response = await fetch('http://127.0.0.1:5000/BudgetPercentage', {
          method: "GET"
      });
      if (!response.ok) {
          throw new Error("Failed to fetch percentage. Status: " + response.status);
      }
      const data = await response.json();
      const percentage = data["percent"];
      const bar = document.getElementById("budgetpercentage");
      bar.style.width = percentage + "%";
      bar.innerText = `${percentage.toFixed(2)}% of the total budget limit used`;
      bar.setAttribute("aria-valuenow", percentage); 
  } catch (error) {
      console.error("Error fetching budget percentage:", error);
  }
}


document.addEventListener("DOMContentLoaded", function() {
  getPercentage();
});
