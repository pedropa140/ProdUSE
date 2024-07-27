// Text for typing animation
const textToType = [
  "Establish a consistent study routine to develop a habit of learning.",
  "Break down complex concepts into smaller, manageable chunks for better understanding.",  
  "Utilize active learning techniques such as summarizing, teaching others, and self-testing.",
  "Create organized notes using bullet points, diagrams, and color-coding for clarity.",
  "Set specific, achievable goals to stay motivated and track progress.",
  "Prioritize tasks by importance and urgency to manage time effectively.",
  "Seek clarification from teachers or peers when encountering difficulties.",
  "Take regular breaks during study sessions to maintain focus and prevent burnout.",
  "Practice retrieval exercises like flashcards or quizzes to reinforce learning.",
  "Review previous material periodically to strengthen retention and build connections.",
  "Stay curious and cultivate a growth mindset, embracing challenges as opportunities for growth."
];


// Function to simulate typing effect
let index = 0;
function typeText() {
  let currentText = "";
  let letterIndex = 0;

  const typingInterval = setInterval(() => {
    if (letterIndex < textToType[index].length) {
      currentText += textToType[index].charAt(letterIndex);
      // Add blinking cursor
      document.getElementById("typing-text").innerText = currentText + "|";
      letterIndex++;
    } else {
      clearInterval(typingInterval); // Stop the typing
      setTimeout(eraseText, 1500);
    }
  }, 100);

  function eraseText() {
    const eraseInterval = setInterval(() => {
      if (currentText.length > 0) {
        currentText = currentText.slice(0, -1);
        document.getElementById("typing-text").innerText = currentText + "|";
      } else {
        clearInterval(eraseInterval);
        document.getElementById("typing-text").innerText = ""; // Clear the text
        index = (index + 1) % textToType.length; // Move to the next string
        letterIndex = 0; // Reset letterIndex for the next word
        currentText = ""; // Reset currentText for the next word
        setTimeout(typeText, 500);
      }
    }, 50);
  }
}

// Initiate typing animation
window.onload = typeText;
