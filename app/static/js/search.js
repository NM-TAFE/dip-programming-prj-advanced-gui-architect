const inputElement = document.getElementById('search-in');
const searchButton = document.getElementById("search-button");
const searchResults = document.querySelectorAll(".continue-items");


searchButton.addEventListener('click', () => {
     const query = inputElement.value.trim().toLowerCase();
     searchResults.forEach((item) => {
         // Do something with the item, e.g., log its text content
         if (item.textContent.toLowerCase().includes(query)){
             item.classList.remove('hidden');
            }
            else
            {
                item.classList.add('hidden');
            }
        if (query === "") {
            item.classList.remove('hidden');
        }
        });

});
  
