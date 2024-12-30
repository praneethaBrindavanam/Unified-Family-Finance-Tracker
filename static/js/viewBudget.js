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
      const msg = document.createElement("p");
      msg.innerText = "Budget deleted successfully";
      msg.style.color = "green";
      const container = document.getElementsByClassName("alert-container")[0];
      container.appendChild(msg);
      setTimeout(() => {
        msg.remove();
        function reload() {
          window.location.reload();
        }
        reload();
      }, 1000);
    } else {
      alert("Failed to delete the budget.");
    }
  }
}

function openUpdateModal(
  budgetId,
  budgetName,
  budgetAmount,
  category,
  startDate,
  endDate
) {
  document.getElementById("updateSection").style.display = "flex";
  document.getElementById("budgetId").value = budgetId || "";
  document.getElementById("budgetAmount").value = budgetAmount || "";
  document.getElementById("budgetCategory").value = category || 1;
  document.getElementById("startDate").value = startDate || "";
  document.getElementById("endDate").value = endDate || "";
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
  const response = await fetch("http://127.0.0.1:5000/Budget", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updatedData),
  });
  console.log("Updated Data:", updatedData, response.message);
  const res = await response.json();

  if (res.message) {
    const msg = document.createElement("p");
    msg.innerText = "Budget updated successfully";
    msg.style.color = "yellow";
    const container = document.getElementsByClassName("alert-container")[0];
    container.appendChild(msg);
    setTimeout(() => {
      msg.remove();
      function reload() {
        window.location.reload();
      }
      reload();
    }, 1000);
  } else {
    alert("Failed to delete the budget.");
  }

  closeUpdateModal(); // Close the modal
}

function closeUpdateModal() {
  document.getElementById("updateSection").style.display = "none"; // Hide modal
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
          const msg=document.createElement("p")
          msg.innerText="Budget Renew Successfully for the Same Duration"
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