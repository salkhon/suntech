const compareToggler = document.getElementById("cmpr-btn");
/** @type {HTMLElement} */
const compareTogglerClose = document.querySelector("span.cmpr-toggler");
const comparePanel = document.getElementById("cmpr-panel");

const comparePanelClearAll = document.getElementById("cmpr-clear-all");

/** @type {HTMLButtonElement} */
const compareNowButton = document.querySelector("#compare-now-btn");
compareNowButton.disabled = true;

compareToggler.onclick = function () {
	compareToggler.classList.toggle("close");
	compareTogglerClose.classList.toggle("open");
	comparePanel.classList.toggle("open");
};

compareTogglerClose.onclick = function () {
	compareToggler.click();
};

// Product class already exists from cart.js
class ComparePanel {
	SESSION_COMPARE_PRODUCT_NAME = "compareProductName";
	SESSION_COMPARE_PRODUCT_IMG = "compareProductImg";

	/**
	 * @param {HTMLElement} comparePanelElem
	 */
	constructor(comparePanelElem) {
		/** @type {Product[]} */
		this.products = this.#retrieveProductsFromSessionStorage();
		this.comparePanelElem = comparePanelElem;

		this.renderComparePanelElem();
	}

	#retrieveProductsFromSessionStorage() {
		const idToProductMap = new Map();

		for (const key in sessionStorage) {
			if (key.startsWith("compareProduct")) {
				const sessionProductId = parseInt(key.match(/\d+/)[0]);

				if (!idToProductMap.get(sessionProductId)) {
					idToProductMap.set(sessionProductId, new Product());
					idToProductMap.get(sessionProductId).id = sessionProductId;
				}

				const product = idToProductMap.get(sessionProductId);

				if (key.startsWith(this.SESSION_COMPARE_PRODUCT_NAME)) {
					product.name = sessionStorage.getItem(
						this.SESSION_COMPARE_PRODUCT_NAME + product.id
					);
				} else if (key.startsWith(this.SESSION_COMPARE_PRODUCT_IMG)) {
					product.img = sessionStorage.getItem(
						this.SESSION_COMPARE_PRODUCT_IMG + product.id
					);
				}
			}
		}

		const products = [];

		idToProductMap.forEach((val, key) => {
			products.push(val);
		});

		return products;
	}

	/**
	 * @param {Product} product
	 */
	#buildCompareProduct(product) {
		const compareProductDivElem = document.createElement("div");
		compareProductDivElem.classList.add("item");
		compareProductDivElem.innerHTML = `
        <div class="info">
            <div class="image"><img src=${product.img} width="47" height="47"></div>
            <div class="name">${product.name}</div>
        </div>
        <span class="remove" title="Remove"><i class="material-icons" aria-hidden="true">delete</i></span>
        `;

		compareProductDivElem
			.querySelector("span.remove")
			.addEventListener(
				"click",
				this.removeCompareElement.bind(this, product)
			);

		return compareProductDivElem;
	}

	/**
	 * @param {Element} productElem
	 */
	addToComparePanel(productElem) {
		if (this.products.length >= 2) {
			return;
		}

		// @ts-ignore
		const productId = parseInt(productElem.dataset.productId);

		const productInList = this.products.find(
			(productInList) => productInList.id === productId
		);

		if (productInList) {
			return;
		} else {
			const product = new Product(productId);
			product.name =
				productElem.querySelector("h4.p-item-name a").textContent;
			product.img = productElem
				.querySelector("img")
				.src.replace("http://localhost:5000", "");
			product.elem = productElem;

			this.products.push(product);
		}

		this.#updateSessionStorage();
		this.renderComparePanelElem();
		alert("Product has been added to compare!");
	}

	/**
	 * @param {Product} product
	 */
	removeCompareElement(product) {
		const index = this.products.findIndex(
			(productInList) => productInList.id === product.id
		);
		this.products.splice(index, 1);

		this.#updateSessionStorage();
		this.renderComparePanelElem();
	}

	#updateSessionStorage() {
		this.#clearCompareSession();
		this.products.forEach((product) => {
			sessionStorage.setItem(
				this.SESSION_COMPARE_PRODUCT_NAME + product.id,
				product.name
			);
			sessionStorage.setItem(
				this.SESSION_COMPARE_PRODUCT_IMG + product.id,
				"" + product.img
			);
		});
	}

	renderComparePanelElem() {
		const comparePanelContentDiv =
			this.comparePanelElem.querySelector("div.content");
		comparePanelContentDiv.replaceChildren();

		this.products.forEach((product) => {
			const compareProductElem = this.#buildCompareProduct(product);
			comparePanelContentDiv.appendChild(compareProductElem);
		});

		const compareTogglerCounter =
			compareToggler.querySelector("span.counter");
		compareTogglerCounter.textContent = "" + this.products.length;
		compareNowButton.disabled = this.products.length < 2;
	}

	#clearCompareSession() {
		for (const key in sessionStorage) {
			if (key.startsWith("compareProduct")) {
				sessionStorage.removeItem(key);
			}
		}
	}

	clearComparePanel() {
		this.products = [];
		this.#clearCompareSession();
		this.renderComparePanelElem();
	}
}

const comparePanelJS = new ComparePanel(comparePanel);

const addToCompareButtons = document.querySelectorAll("span.btn-compare");
addToCompareButtons.forEach((button) => {
	// @ts-ignore
	button.onclick = function () {
		const productElem = button.closest("div.p-item");
		comparePanelJS.addToComparePanel(productElem);
	};
});

comparePanelClearAll.onclick = function () {
	comparePanelJS.clearComparePanel();
};

compareNowButton.onclick = async function (/** @type { Event } */ event) {
	event.preventDefault();

	// @ts-ignore
	if (this.disabled) {
		return;
	}

	const urlWithQueryParams =
		"http://localhost:5000/product/compare?" +
		new URLSearchParams({
			prod1: comparePanelJS.products[0].id.toString(),
			prod2: comparePanelJS.products[1].id.toString(),
		});

	window.location.href = urlWithQueryParams;
};
