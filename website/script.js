// Get references to the number input field and the button
const rx = document.getElementById("rx");
const ry = document.getElementById("ry");
const rz = document.getElementById("rz");
const step = document.getElementById("movestep");

function xpositive() {
  rx.value = parseInt(rx.value) + parseInt(step.value);
}

function xnegitive() {
  rx.value = parseInt(rx.value) - parseInt(step.value);
}

function ypositive() {
  ry.value = parseInt(ry.value) + parseInt(step.value);
}

function ynegitive() {
  ry.value = parseInt(ry.value) - parseInt(step.value);
}

function zpositive() {
  rz.value = parseInt(rz.value) + parseInt(step.value);
}

function znegitive() {
  rz.value = parseInt(rz.value) - parseInt(step.value);
}

const moveButtons = document.querySelectorAll(".button");
moveButtons.forEach((button) => {
  button.addEventListener("click", () => {
    makePostRequest();
  });
});

rx.addEventListener("input", makePostRequest);
ry.addEventListener("input", makePostRequest);
rz.addEventListener("input", makePostRequest);

function makePostRequest() {
  const data = {
    rx: rx.value,
    ry: ry.value,
    rz: rz.value
  };

  fetch("http://localhost:5000/move", {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json"
    }
  })
    .then((response) => {
      if (response.ok) {
        console.log("Move request sent successfully.");
        // Handle the success case
      } else {
        console.log("Failed to send move request.");
        // Handle the failure case
      }
    })
    .catch((error) => {
      console.error("Error sending move request:", error);
      // Handle the error case
    });
}

const darkarmFileInput = document.getElementById("darkarmFile");

function upload() {
  const file = darkarmFileInput.files[0];
  if (file) {
    const formData = new FormData();
    formData.append("darkarmFile", file);
    fetch("https://api.example.com/upload", {
      method: "POST",
      body: formData
    })
      .then((response) => {
        if (response.ok) {
          console.log("File uploaded successfully.");
          // Handle the success case
        } else {
          console.log("File upload failed.");
          // Handle the failure case
        }
      })
      .catch((error) => {
        console.error("Error uploading file:", error);
        // Handle the error case
      });
  }
}
