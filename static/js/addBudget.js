    //currently hardcoding name
    document.addEventListener("DOMContentLoaded", () => {
        document.getElementById("addBudget").addEventListener('click', async () => {
            try {
                const response = await fetch("http://127.0.0.1:5000/Budget", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        category_id: document.getElementById("Category").value,
                        limit: document.getElementById("limit").value,
                        start_date: document.getElementById("start_date").value,
                        end_date: document.getElementById("end_date").value,
                        user_id: 2
                    })
                });
                if(response.status==201){
                    const msg=document.createElement("p")
                    msg.innerText="Budget Created Successfully"
                    document.getElementsByClassName("input_container")[0].appendChild(msg)
                    setTimeout(() => {
                        msg.remove();
                        window.location.href='/budgethome';
                    }, 1500);
                }
            } catch (err) {
                console.log(err);
            }
        });
    });