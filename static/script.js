document.getElementById('order-form').addEventListener('submit', function(event) {
  event.preventDefault();
  
  const action = document.getElementById('action').value;
  const symbol = document.getElementById('symbol').value;
  const quantity = parseInt(document.getElementById('quantity').value, 10);

  // Debugging: Log the values being sent
  console.log('Action:', action);
  console.log('Symbol:', symbol);
  console.log('Quantity:', quantity);

  fetch('/order', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ side: action, symbol: symbol, quantity: quantity })
  })
  .then(response => {
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
  })
  .then(data => {
      logToConsole(`Order Action: ${action}, Symbol: ${symbol}, Quantity: ${quantity}`);
      logToConsole(`Response: ${JSON.stringify(data)}`);
      document.getElementById('order-confirmation').classList.remove('hidden');
  })
  .catch(error => logToConsole(`Error: ${error.message}`));
});

document.getElementById('subscribe-market-data').addEventListener('click', function() {
  fetch('/subscribe', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ symbol: 'USD/BRL' })
  })
  .then(response => response.json())
  .then(data => {
      logToConsole(`Subscribed to market data: USD/BRL`);
      logToConsole(`Response: ${JSON.stringify(data)}`);
      document.getElementById('market-status').textContent = "Subscribed to market data.";
      document.getElementById('unsubscribe-market-data').disabled = false;
  })
  .catch(error => logToConsole(`Error: ${error}`));
});

document.getElementById('unsubscribe-market-data').addEventListener('click', function() {
  fetch('/unsubscribe', {
      method: 'POST'
  })
  .then(response => response.json())
  .then(data => {
      logToConsole(`Unsubscribed from market data`);
      logToConsole(`Response: ${JSON.stringify(data)}`);
      document.getElementById('market-status').textContent = "No market data subscribed yet.";
      document.getElementById('unsubscribe-market-data').disabled = true;
  })
  .catch(error => logToConsole(`Error: ${error}`));
});

// Function to update console log
function logToConsole(message) {
  const consoleOutput = document.getElementById('console-output');
  const newLog = document.createElement('p');
  newLog.textContent = message;
  consoleOutput.appendChild(newLog);

  // Auto-scroll to the bottom of the console
  const consoleDiv = document.getElementById('console');
  consoleDiv.scrollTop = consoleDiv.scrollHeight;
}
