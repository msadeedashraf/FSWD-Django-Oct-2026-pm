let myBalance = 1500;
document.getElementById("balance").innerHTML = myBalance;

function makeDeposit() {
  const amount = parseFloat(document.getElementById("depositAmount").value);
  myBalance += amount;
  document.getElementById("balance").innerHTML = myBalance;

  addTransaction("Credit", amount);
}

function makeWithdrawal() {
  const amount = parseFloat(document.getElementById("withdrawAmount").value);
  myBalance -= amount;
  document.getElementById("balance").innerHTML = myBalance;
  addTransaction("Debit", amount);
}

function addTransaction(type, amount) {
  const transactionList = document.getElementById("transaction");
  const transactionItem = document.createElement("li");
  //transactionItem.textContent = type + ": $ " +amount + " | Balance: $" +myBalance;
  //With String Interpolation
  transactionItem.textContent = `${type} : $ ${amount} | Balance: $ ${myBalance}`;

  transactionList.appendChild(transactionItem);
}
