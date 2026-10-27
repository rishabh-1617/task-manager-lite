
const taskList = document.getElementById("task-list");
const message = document.getElementById("message");

// Load tasks from the FastAPI backend.
async function loadTasks() {
    try {
        message.textContent = "Loading tasks...";

        const response = await fetch("/api/tasks");

        if (!response.ok) {
            throw new Error("Could not load tasks.");
        }

        const tasks = await response.json();

        taskList.replaceChildren();

        
if (tasks.length === 0) {
    const item = document.createElement("li");
    item.textContent = "No tasks yet. Add your first task!";
    taskList.appendChild(item);
} else {
    tasks.forEach((task) => {
        const item = document.createElement("li");

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = Boolean(task.completed);
        checkbox.setAttribute(
            "aria-label",
            `Mark ${task.title} as completed`
        );

        const title = document.createElement("span");
        title.textContent = task.title;

        if (checkbox.checked) {
            title.style.textDecoration = "line-through";
            title.style.color = "#6b7280";
        }

        checkbox.addEventListener("change", async () => {
            await toggleTask(task, checkbox, title);
        });

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => editTask(task));

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "Delete";
        deleteButton.style.background = "#dc2626";
        deleteButton.addEventListener("click", () => deleteTask(task));

        item.append(checkbox, title, editButton, deleteButton);
        taskList.appendChild(item);
    });
}


        message.textContent = `${tasks.length} task(s) loaded.`;
    } catch (error) {
        message.textContent = error.message;
    }
}

// Run when the page opens.
loadTasks();




const taskForm = document.getElementById("task-form");
const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");

taskForm.addEventListener("submit", async (event) => {
    // Prevent the browser from reloading the page.
    event.preventDefault();

    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();

    if (!title) {
        message.textContent = "Please enter a task title.";
        return;
    }

    try {
        message.textContent = "Adding task...";

        const response = await fetch("/api/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: title,
                description: description
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "Could not create the task."
            );
        }

        // Read the task returned by the backend.
        const newTask = await response.json();

        // Clear the form after successful creation.
        taskForm.reset();

        // Reload tasks to show the new task.
        await loadTasks();

        message.textContent =
            `Task "${newTask.title}" added successfully!`;

    } catch (error) {
        message.textContent = error.message;
    }
});


async function toggleTask(task, checkbox, title) {
    const previousState = !checkbox.checked;

    try {
        message.textContent = "Updating task...";

        const response = await fetch(`/api/tasks/${task.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: task.title,
                description: task.description,
                completed: checkbox.checked
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "Could not update task."
            );
        }

        const updatedTask = await response.json();

        task.completed = updatedTask.completed;

        title.style.textDecoration =
            Boolean(updatedTask.completed) ? "line-through" : "none";

        title.style.color =
            Boolean(updatedTask.completed) ? "#6b7280" : "";

        checkbox.checked = Boolean(updatedTask.completed);
        message.textContent = "Task status updated successfully.";

    } catch (error) {
        checkbox.checked = previousState;
        message.textContent = error.message;
    }
}


async function editTask(task) {
    const newTitle = prompt("Edit task title:", task.title);

    // Stop if the user clicks Cancel.
    if (newTitle === null) {
        return;
    }

    const title = newTitle.trim();

    if (!title) {
        message.textContent = "Task title cannot be empty.";
        return;
    }

    const newDescription = prompt(
        "Edit task description:",
        task.description || ""
    );

    if (newDescription === null) {
        return;
    }

    try {
        message.textContent = "Saving changes...";

        const response = await fetch(`/api/tasks/${task.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: title,
                description: newDescription.trim(),
                completed: Boolean(task.completed)
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "Could not edit task."
            );
        }

        await response.json();

        await loadTasks();

        message.textContent = "Task updated successfully.";

    } catch (error) {
        message.textContent = error.message;
    }
}

async function deleteTask(task) {
    if (!confirm(`Delete "${task.title}"?`)) {
        return;
    }

    try {
        message.textContent = "Deleting task...";

        const response = await fetch(`/api/tasks/${task.id}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error("Could not delete task.");
        }

        await loadTasks();
        message.textContent = "Task deleted successfully.";
    } catch (error) {
        message.textContent = error.message;
    }
}