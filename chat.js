const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Job-related responses (strictly career-focused)
const jobResponses = {
  'resume': "Tailor your resume to the job description using keywords. Highlight achievements with metrics (e.g., 'Increased sales by 30%').",
  'cover letter': "Address the hiring manager by name, mention the job title, and explain why you're a fit. Use 3-4 paragraphs max.",
  'interview': "Practice the STAR method (Situation, Task, Action, Result) for behavioral questions. Research the company beforehand.",
  'salary negotiation': "Research industry rates on Glassdoor. Say: 'Based on my skills and market data, I was expecting [range].'",
  'career change': "Identify transferable skills. Take online courses/certifications to fill gaps. Network in your target industry.",
  'linkedin': "Use a professional photo, write a headline with keywords, and summarize your top achievements in the 'About' section.",
  'quit job': "Give a 2-week notice in writing. Stay professional—say you’re pursuing growth opportunities, even if you’re unhappy.",
  'promotion': "Document your achievements, ask for feedback, and express interest in growth. Align your goals with company needs.",
  'remote work': "Set up a dedicated workspace, over-communicate with your team, and use tools like Slack/Trello to stay organized.",
  'default': "I only answer job-related questions (resumes, interviews, careers). Try: 'How do I prepare for a technical interview?'"
};

// Add a message to the chat
function addMessage(sender, text) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message', `${sender}-message`);
  messageDiv.textContent = text;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Bot response logic
function getBotResponse(userText) {
  const lowerText = userText.toLowerCase();
  
  // Check for job-related keywords
  if (lowerText.includes('resume')) return jobResponses['resume'];
  if (lowerText.includes('cover letter')) return jobResponses['cover letter'];
  if (lowerText.includes('interview')) return jobResponses['interview'];
  if (lowerText.includes('salary') || lowerText.includes('negotiation')) return jobResponses['salary negotiation'];
  if (lowerText.includes('career change') || lowerText.includes('switch job')) return jobResponses['career change'];
  if (lowerText.includes('linkedin')) return jobResponses['linkedin'];
  if (lowerText.includes('quit') || lowerText.includes('resign')) return jobResponses['quit job'];
  if (lowerText.includes('promotion')) return jobResponses['promotion'];
  if (lowerText.includes('remote work') || lowerText.includes('work from home')) return jobResponses['remote work'];
  
  // Reject off-topic questions
  return jobResponses['default'];
}

// Send button click handler
sendBtn.addEventListener('click', () => {
  const userText = userInput.value.trim();
  if (userText) {
    addMessage('user', userText);
    const botResponse = getBotResponse(userText);
    setTimeout(() => addMessage('bot', botResponse), 500);
    userInput.value = '';
  }
});

// Allow Enter key to send
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendBtn.click();
});

// Initial bot greeting
addMessage('bot', "Hi! I'm your Job Assistant. Ask me about resumes, interviews, or career advice.");