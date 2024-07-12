document.addEventListener('DOMContentLoaded', function () {
  let chatHistory = '';

  const chatbotIcon = document.createElement('div');
  chatbotIcon.classList.add('chatbot-icon');
  document.body.appendChild(chatbotIcon);

  const chatbotDialog = document.createElement('div');
  chatbotDialog.classList.add('chatbot-dialog');
  chatbotDialog.style.display = 'none'; // Ensure dialog is hidden initially
  document.body.appendChild(chatbotDialog);

  const chatbotHeader = document.createElement('div');
  chatbotHeader.classList.add('chatbot-header');
  chatbotDialog.appendChild(chatbotHeader);

  const closeButton = document.createElement('button');
  closeButton.classList.add('chatbot-close');
  closeButton.innerHTML = '&times;';
  chatbotHeader.appendChild(closeButton);

  const chatbotMessages = document.createElement('div');
  chatbotMessages.classList.add('chatbot-messages');
  chatbotDialog.appendChild(chatbotMessages);

  const inputContainer = document.createElement('div');
  inputContainer.classList.add('chatbot-input-container');
  chatbotDialog.appendChild(inputContainer);

  const chatbotInput = document.createElement('input');
  chatbotInput.classList.add('chatbot-input');
  chatbotInput.setAttribute('type', 'text');
  chatbotInput.setAttribute('placeholder', 'type question here');
  inputContainer.appendChild(chatbotInput);

  const submitButton = document.createElement('button');
  submitButton.classList.add('chatbot-submit-icon');
  submitButton.addEventListener('click', function() {
    chatbotInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
  });
  inputContainer.appendChild(submitButton);

  const userId = document.getElementById('chatbot-button').getAttribute('data-user-id'); // Retrieve user ID from data attribute

  chatbotIcon.addEventListener('click', () => {
    chatbotIcon.style.display = 'none';
    chatbotDialog.style.display = 'flex';
    chatbotDialog.style.opacity = '0'; // Set initial opacity for fade-in
    chatHistory = ''; // Reset chat history
    chatbotMessages.innerHTML = ''; // Clear previous messages
    setTimeout(() => {
      chatbotDialog.style.opacity = '1'; // Fade-in effect
      addMessage('Hi '+userId+', ask me any question about your data?"', 'bot');
    }, 0);
  });

  closeButton.addEventListener('click', () => {
    chatbotDialog.style.display = 'none';
    chatbotIcon.style.display = 'block';
    chatHistory = ''; // Reset chat history
  });

  chatbotInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      const userMessage = chatbotInput.value;
      if (userMessage.trim() !== '') {
        addMessage(userMessage, 'user');
        submitQuestion(userMessage);
      }
      chatbotInput.value = '';
    }
  });

  function addMessage(text, sender, isTemporary = false) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('chatbot-message', sender);

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('chatbot-bubble', sender);
    if (isTemporary) {
      const ellipsisSpan = document.createElement('span');
      ellipsisSpan.classList.add('chatbot-ellipsis');
      messageBubble.appendChild(ellipsisSpan);
      messageBubble.innerHTML = 'thinking...';
    } else {
      messageBubble.innerHTML = text;
    }

    const icon = document.createElement('div');
    if (sender === 'bot') {
      icon.classList.add('chatbot-icon-bot');
      messageContainer.appendChild(icon);
      messageContainer.appendChild(messageBubble);
      if (!isTemporary) {
        chatHistory += `Bot: ${text}\n`; // Append bot response to chat history
      }
    } else {
      icon.classList.add('chatbot-icon-user');
      messageContainer.appendChild(messageBubble);
      messageContainer.appendChild(icon);
      chatHistory += `User: ${text}\n`; // Append user question to chat history
    }

    chatbotMessages.appendChild(messageContainer);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    return messageBubble;
  }

  function submitQuestion(question) {
    const tempBubble = addMessage('', 'bot', true);

    const requestOptions = {
      method: 'POST',
      headers: { 
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY' 
    },
      
      body: JSON.stringify({ user_id: userId, question: `${chatHistory}User: ${question}` })  // Include user ID in the request body
    };

    fetch('GOOGLE_CLOUD_FUNCTION_ENDPOINT', requestOptions)
      .then((response) => response.text())
      .then((data) => {
        console.log('Received data:', data);
        tempBubble.innerHTML = data; // Replace the temporary bubble content with the actual response
        chatHistory += `Bot: ${data}\n`; // Append bot response to chat history
      })
      .catch((error) => {
        console.error('Error:', error);
        tempBubble.innerHTML = 'Sorry, I could not get the answer. Please try again later.';
      });
  }
});
