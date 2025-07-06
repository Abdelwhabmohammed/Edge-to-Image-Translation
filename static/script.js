// Event listener for sketch form submission
document.getElementById("sketchForm").onsubmit = async function(event) {
    event.preventDefault();

    const formData = new FormData();
    const sketchFile = document.getElementById("sketch").files[0];
    formData.append("sketch", sketchFile);

    const response = await fetch("/generate_sketch", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        const responseData = await response.json();
        const inputImageUrl = URL.createObjectURL(sketchFile);
        document.getElementById("inputImage").src = inputImageUrl;

        document.getElementById("resultImage").src = responseData.generatorImage;
    } else {
        console.error("Failed to generate image from sketch.");
    }
};

// Event listener for prompt form submission
document.getElementById("promptForm").onsubmit = async function(event) {
    event.preventDefault();

    const promptText = document.getElementById("prompt").value;
    const formData = new FormData();
    formData.append("prompt", promptText);

    const response = await fetch("/generate_prompt", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        const responseData = await response.json();
        if (responseData.promptImage) {
            document.getElementById("generatedFromPrompt").src = responseData.promptImage;
        } else {
            alert("Image generation failed. Please try again.");
        }
    } else {
        console.error("Failed to generate image from prompt.");
        alert("Image generation failed. Please try again.");
    }
};