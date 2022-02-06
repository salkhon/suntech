const orderOverviewTableBody = document.querySelector("tbody");
/** @type {HTMLFormElement} */
const checkoutForm = document.querySelector("form#checkout-form");

let subTotal = 0.0;

cartJS.products.forEach((product) => {
	const tableRow = document.createElement("tr");
	tableRow.innerHTML = `
        <td class="name">
            <a
                href="http://localhost:5000/product/${product.id}"
                >${product.name}</a
            >
            <div class="options"></div>
        </td>
        <td class="rs-none">${product.price}৳</td>
        <td class="rs-none">${product.count}</td>
        <td class="price text-right">
            ${product.price * product.count}৳
        </td>								
    `;
	orderOverviewTableBody.appendChild(tableRow);
	subTotal += product.price * product.count;
});

const homeDelivery = 60;

orderOverviewTableBody.innerHTML += `
    <tr class="total">
        <td colspan="3" class="text-right"><strong>Sub-Total:</strong></td>
        <td class="text-right"><span class="amount">${subTotal}৳</span></td>
    </tr>
    <tr class="total">
        <td colspan="3" class="text-right"><strong>Home Delivery:</strong></td>
        <td class="text-right"><span class="amount">${homeDelivery}৳</span></td>
    </tr>
    <tr class="total">
        <td colspan="3" class="text-right"><strong>Total:</strong></td>
        <td class="text-right"><span class="amount">${
			subTotal + homeDelivery
		}৳</span></td>
    </tr>
`;

checkoutForm.onsubmit = async (/** @type { Event } */ event) => {
	event.preventDefault();
	const formdata = new FormData(checkoutForm);
	const formdataJSON = Object.fromEntries(formdata.entries());

	fetch("http://localhost:5000/sale/checkout", {
		method: "POST",
		redirect: "follow",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			products: cartJS.products.map((product) => {
				return {
					id: product.id,
					count: product.count,
				};
			}),
			formdata: formdataJSON,
		}),
	})
		.then((response) => {
			cartJS.clearCart();
			if (response.redirected) {
				window.location.href = response.url;
			}
		})
		.catch((err) => console.log("Could not send checkout", err));
};
