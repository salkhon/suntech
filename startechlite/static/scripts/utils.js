
function changeImage(obj){
	main_img = document.getElementById("main_img");
	main_img.setAttribute('src', obj.getAttribute('lnk'));
	return false;

}

function price_range(slider){
	var output = document.getElementById("range-from");
	output.value = 'Tk.'+slider.value;
	console.log('Did something')
}

var search_input = document.getElementById("main_search");

search_input.addEventListener("keyup",async function (/** @type { Event } */ event) {

  if (event.keyCode === 13) {
    event.preventDefault();

    const urlWithSearchString = "http://localhost:5000/search?" + new URLSearchParams( {
		search_string: search_input.value
	});

	window.location.href = urlWithSearchString;
  }
});

// var search_button = document.getElementById('search_button')
// search_button.onclick = async function (/** @type { Event } */ event) {

// 	const urlWithSearchString = "http://localhost:5000/search?" + new URLSearchParams( {
// 		search_string:'Nitro Mama'
// 	});

// 	window.location.href = urlWithSearchString;
// };
