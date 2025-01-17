document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("addBudget").addEventListener("click", async () => {
        try {
            const start_date = new Date(document.getElementById("start_date").value).getTime();
            const end_date = new Date(document.getElementById("end_date").value).getTime();
            if (end_date < Date.now() || start_date < Date.now() || start_date >= end_date) {
                alert("Invalid Dates: Ensure start date is earlier than end date and both are in the future.");
                return;
            }

            const category_id = document.getElementById("Category").value;
            const limit = document.getElementById("limit").value;
            if (!category_id || !limit || isNaN(limit) || limit <= 0) {
                alert("Invalid category or limit");
                return;
            }

            console.log("Submitting Budget:", { category_id, limit, start_date, end_date });

            const response = await fetch("http://127.0.0.1:5000/Budget", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    category_id,
                    limit,
                    start_date:document.getElementById("start_date").value,
                    end_date:document.getElementById("end_date").value,
                    user_id: null, 
                }),
            });

            if (response.status == 201) {
                const msg = document.getElementById("message") || document.createElement("p");
                msg.id = "message";
                msg.innerText = "Budget Created Successfully";
                document.getElementsByClassName("input_container")[0].appendChild(msg);

                setTimeout(() => {
                    msg.remove();
                    window.location.href = "/budgethome";
                }, 1500);
            }
        } catch (err) {
            console.error("Error creating budget:", err);
            alert("An error occurred. Please try again.");
        }
    });
});
