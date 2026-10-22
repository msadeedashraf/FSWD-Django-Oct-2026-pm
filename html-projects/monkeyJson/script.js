//alert("Hi");

fetch(
  "https://raw.githubusercontent.com/jamesmontemagno/app-monkeys/master/MonkeysApp/monkeydata.json"
) //// Replace with your actual JSON file or API endpoint URL
  .then((response) => response.json())
  .then((data) => {
    console.log(data); //testing to see if the data is pickedup from json file or not
    const monkeys = data;
    getmonkeys(monkeys);
  })
  .catch((error) =>
    console.error("Error fetching json data, please check your path", error)
  );

function getmonkeys(monkeys) {
  console.log(monkeys);

  let myHtml = "";
  for (a = 0; a < monkeys.length; a++) {
    myHtml += `
 
   <div class="card mb-3" style="max-width: 540px;">
            <div class="row g-0">
              <div class="col-md-4">
                <img src=${monkeys[a].Image} class="img-fluid rounded-start" alt="...">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <h5 class="card-title">${monkeys[a].Name}</h5>
                  <p class="card-text">${monkeys[a].Details}</p>
                  <p class="card-text"><small class="text-body-secondary">Last updated 3 mins ago</small></p>
                </div>
              </div>
            </div>
          </div>
  
 
  `;
  }

  //console.log(myHtml);

  document.getElementById("demo").innerHTML = myHtml;
}
