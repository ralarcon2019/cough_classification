document.addEventListener("DOMContentLoaded", () => {
  const recordButton = document.getElementById("recordButton"); // Ensure this matches the button ID in your HTML
  let mediaRecorder;
  let audioChunks = [];

  if (recordButton) {
    recordButton.addEventListener("click", async () => {
      // If mediaRecorder is not initialized or inactive, start recording
      if (!mediaRecorder || mediaRecorder.state === "inactive") {
        try {
          // Request access to the user's microphone
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

          // Initialize MediaRecorder
          mediaRecorder = new MediaRecorder(stream);

          // Collect audio chunks when data is available
          mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
          };

          // Handle the stop event and upload audio
          mediaRecorder.onstop = async () => {
            recordButton.innerText = "Record Audio"; // Reset button text

            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            const formData = new FormData();
            formData.append("audio_file", audioBlob, "recording.wav");

            try {
              const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
              const csrfToken = csrfTokenElement.getAttribute("content");

              const response = await fetch("/users/upload-audio/", {
                method: "POST",
                headers: {
                  "X-CSRFToken": csrfToken,
                },
                body: formData,
              });

              if (response.ok) {
                const data = await response.json();
                alert("Audio uploaded successfully! File URL: " + data.file_url);
              } else {
                const data = await response.json();
                alert("Error uploading audio: " + (data.error || "Unknown error."));
              }
            } catch (err) {
              console.error("Error uploading audio:", err);
              alert("Failed to upload audio. Please try again.");
            } finally {
              // Ensure the recorder stops no matter what
              if (mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
              }
              recordButton.innerText = "Record Audio"; // Reset the button text
            }
          };

          // Clear any existing audio chunks and start recording
          audioChunks = [];
          mediaRecorder.start();
          recordButton.innerText = "Stop Recording"; // Update button text
        } catch (err) {
          console.error("Error accessing microphone:", err);
          alert("Unable to access your microphone. Please check your settings.");
        }
      } else if (mediaRecorder.state === "recording") {
        // If recording is in progress, stop the mediaRecorder
        mediaRecorder.stop();
      }
    });
  } else {
    console.error("Record button not found on the page.");
  }
});
