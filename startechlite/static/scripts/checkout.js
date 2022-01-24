const orderOverviewTableBody = document.querySelector("tbody");
let subTotal = 0.0;

cartJS.products.forEach((product) => {
	const tableRow = document.createElement("tr");
	tableRow.innerHTML = `
        <td class="name">
            <a
                href="http://localhost:5000/product/${product.handle}"
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

const totalTableRow = document.createElement("tr");
totalTableRow.innerHTML = `
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
orderOverviewTableBody.appendChild(totalTableRow);
