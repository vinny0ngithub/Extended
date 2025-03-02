// Add event listener for the send button
document.getElementById("send-button").addEventListener("click", sendMessage);

// Add event listener for the Enter key
document.getElementById("user-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Add event listener for file upload
// document.getElementById("file-upload").addEventListener("change", handleFileUpload);

// Function to send the message
function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() !== "") {
        displayMessage(userInput, "user");
        document.getElementById("user-input").value = "";
        fetchResponse(userInput);
    }
}

// Function to display the message
function displayMessage(text, sender) {
    const messages = document.getElementById("messages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = text; // Use innerHTML to render HTML content
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Function to fetch the response from the backend
async function fetchResponse(userInput) {
    const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userInput }),
    });
    const data = await response.json();
    displayMessage(data.reply, "bot");
}

// Handle file upload//
const fileInput = document.querySelector("#file-upload");
const uploadButton = document.querySelector(".file-upload-icon"); // The label acts as the button

// Listen for file selection
fileInput.addEventListener("change", async (event) => {
  event.preventDefault();
  const file = fileInput.files[0]; // Get the selected file
  if (!file) {
    alert("Please select a file");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:5000/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error uploading file:", errorData);
      alert("Failed to upload file: " + errorData.error);
    } else {
      const successData = await response.json();
      console.log("File uploaded successfully:", successData);
    }
  } catch (error) {
    console.error("Error:", error);
  }
});




