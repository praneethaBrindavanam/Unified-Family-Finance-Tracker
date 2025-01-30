async function deleteBudget(id) {
  if (confirm("Are you sure?")) {
    const response = await fetch("http://127.0.0.1:5000/Budget", {
      headers: {
        "Content-Type": "application/json",
      },
      method: "DELETE",
      body: JSON.stringify({ budget_id: id }),
    });
    if (response.ok) {
      const msg = document.createElement("div");
      msg.innerHTML='<div class=\"alert alert-danger\" role=\"alert\">Budget deleted successfully</div>'
      const container = document.getElementsByClassName("alert-container")[0];
      container.appendChild(msg);
      setTimeout(() => {
        msg.remove();
        function reload() {
          window.location.reload();
        }
        reload();
      }, 1500);
    } else {
      alert("Failed to delete the budget.");
    }
  }
}

function openUpdateModal(budgetId, category, budgetAmount, startDate, endDate) {
  const modal = new bootstrap.Modal(document.getElementById("updateSection"));
  document.getElementById("budgetId").value = budgetId || "";
  document.getElementById("budgetAmount").value = budgetAmount || "";
  document.getElementById("budgetCategory").value = category || 1;
  document.getElementById("startDate").value = startDate || "";
  document.getElementById("endDate").value = endDate || "";
  modal.show(); // Show the modal using Bootstrap
}

function closeUpdateModal() {
  const modal = bootstrap.Modal.getInstance(document.getElementById("updateSection"));
  modal.hide(); // Hide the modal using Bootstrap
}


// Function to Handle Update Form Submission
async function handleUpdate(event) {
  event.preventDefault(); // Prevent form submission
  const updatedData = {
    budget_id: document.getElementById("budgetId").value,
    limit: document.getElementById("budgetAmount").value,
    category_id: document.getElementById("budgetCategory").value,
    start_date: document.getElementById("startDate").value,
    end_date: document.getElementById("endDate").value,
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/Budget", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedData),
    });

    const res = await response.json();

    if (res.message) {
      const msg = document.createElement("div");
      msg.innerHTML='<div class=\"alert alert-warning\" role=\"alert\">Budget Updated successfully</div>'
      const container = document.getElementsByClassName("alert-container")[0];
      container.appendChild(msg);

      setTimeout(() => {
        msg.remove();
        window.location.reload();
      }, 1000);
    } else {
      alert("Failed to update the budget.");
    }
  } catch (error) {
    console.error("Error updating budget:", error);
    alert("An error occurred. Please try again.");
  }

  closeUpdateModal(); // Close the modal
}



async function renewBudget(category_id,limit,start_date,end_date,user_id){
    const start=new Date(start_date)
    const end=new Date(end_date)

    const new_start_date=new Date(end)
    new_start_date.setDate(end.getDate()+1)

    const duration=end-start;
    const new_end_date=new Date(new_start_date)
    new_end_date.setTime(new_start_date.getTime()+duration)
    try {
      const response = await fetch("http://127.0.0.1:5000/Budget", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({
              category_id,limit,
              start_date:new_start_date.toISOString().split('T')[0],
              end_date:new_end_date.toISOString().split('T')[0],
              user_id:user_id
          })
      });
      if(response.status=201){
          const msg = document.createElement("div");
          msg.innerHTML='<div class=\"alert alert-primary\" role=\"alert\">Budget Renewed for the same duration successfully</div>'
          document.getElementsByClassName("alert-container")[0].appendChild(msg)
          setTimeout(() => {
              msg.remove();
              window.location.reload();
          }, 2000);
      }
  } catch (err) {
      console.log(err);
  }
}

function filterCards() {
  let month = document.getElementById("month-selector").value;
  let category = document.getElementById("category-selector").value;
  let limit = document.getElementById("limit-filter").value;
  let startDate = document.getElementById("start-date-filter").value;
  let user_id = document.getElementById("user-selector").value;

  let cards = document.querySelectorAll("#budgetCards .card");

  cards.forEach(card => {
    let cardCategory = card.querySelector(".card-title").textContent.split(" - ")[0].trim();
    let cardLimit = parseFloat(card.querySelector(".card-title").textContent.split(" - ₹")[1].trim());
    let cardStartDate = card.querySelector(".card-text").textContent.split("Start: ")[1].split(" |")[0].trim();
    let cardUserId = card.querySelector(".card-text:last-of-type").textContent.split("User Name: ")[1].trim();
    console.log(cardCategory,cardLimit,cardStartDate,cardUserId)
    let showCard = true;

    if (month) {
      let cardMonth = new Date(cardStartDate).getMonth() + 1;
      if (cardMonth != month) showCard = false;
    }

    if (user_id && user_id != cardUserId) showCard = false;

    if (category && cardCategory != category) showCard = false;

    if (limit && cardLimit > parseFloat(limit)) showCard = false;

    if (startDate && cardStartDate < startDate) showCard = false;

    card.parentElement.style.display = showCard ? "" : "none";
  });
}

function sortCards() {
  let container = document.getElementById("budgetCards");
  let cards = Array.from(container.querySelectorAll(".col-md-4"));
  let sortOrder = document.getElementById("month-sorter").value;

  if (sortOrder === "") return; // If "None" is selected, exit the function

  let ascending = sortOrder == 1;

  cards.sort((a, b) => {
    let aDate = parseDate(a.querySelector(".card-text").textContent.split("Start: ")[1].split(" |")[0].trim());
    let bDate = parseDate(b.querySelector(".card-text").textContent.split("Start: ")[1].split(" |")[0].trim());

    return ascending ? aDate - bDate : bDate - aDate;
  });

  // Append sorted cards back to the container
  cards.forEach(card => container.appendChild(card));
}

function parseDate(dateString) {
  if (!dateString) return new Date(0); // Handle empty dates by returning oldest date
  let parts = dateString.split('-');  // Assumes format YYYY-MM-DD
  return new Date(parts[0], parts[1] - 1, parts[2]); // Month is zero-based
}
