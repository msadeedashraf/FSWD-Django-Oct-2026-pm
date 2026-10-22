//alert("Hello testing");
let balance = 1000;
document.getElementById("balance").innerHTML = balance;

function toggleTransactionFields() {
  let type = document.getElementById("transactionType").value;

  //console.log(type);
  /*
    if (type == "Deposit")
{
type = "Enter Deposit amount";
}
else
{
type = "Enter withdrawal amount";
}
*/

  //Ternary operator
  //condition ? "TRUE" : "False";
  document.getElementById("amount").placeholder =
    type == "Deposit" ? "Enter deposit amount" : "Enter withdrawal amount";
}

function toggleCustomDescription() {
  let description = document.getElementById("transactionDescription").value;
  let customDescriptionField = document.getElementById("customDescription");

  // console.log(description);
  //console.log(customDescriptionField);
  /*
  if (description === "Other") {
    //console.log(customDescriptionField.classList.remove("hidden"))
    customDescriptionField.classList.remove("hidden");
  } else {
    //console.log(customDescriptionField.classList.add("hidden"))

    customDescriptionField.classList.add("hidden");
  }
    */
  //Ternary operator
  description === "Other"
    ? customDescriptionField.classList.remove("hidden")
    : customDescriptionField.classList.add("hidden");
}

function makeTransaction() {
  let type = document.getElementById("transactionType").value;

  let description = document.getElementById("transactionDescription").value;

  if (description == "Other") {
    description = document.getElementById("customDescription").value;
  } else {
    description = description;
  }

  let myamount = parseFloat(document.getElementById("amount").value);
  //console.log(myamount);

  if (type == "Deposit") {
    deposit(myamount);
  } else {
    withdraw(myamount);
  }

  addTransaction(type, description, myamount);
}

function withdraw(amount) {
  balance -= amount;
  document.getElementById("balance").textContent = balance;
}

function deposit(amount) {
  balance += amount;
  document.getElementById("balance").textContent = balance;
}

function addTransaction(type, description, amount) {
  let transactionList = document.getElementById("transactions");

  let date = new Date().toLocaleString();
  let amountClass = type == "Deposit" ? "credit" : "debit";

  let myhtml = `<tr>
            <td>${date}</td>
            <td>${description}</td>
            <td class="${amountClass}" >${amount}</td>
            <td>${balance}</td>
          </tr>`;

  transactionList.innerHTML += myhtml;
}


/*
function addTransaction(type, description, amount) {
    const transactionList = document.getElementById("transactions");
    const transactionRow = document.createElement("tr");
    const date = new Date().toLocaleString();
    const amountClass = type === "Deposit" ? "credit" : "debit";

    transactionRow.innerHTML = `
      <td>${date}</td>
      <td>${description}</td>
      <td class="${amountClass}">$${amount}</td>
      <td>$${balance}</td>
    `;
    transactionList.appendChild(transactionRow);
  }
*/