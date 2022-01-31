const cartToggler = document.getElementById("cart");
const cartCloseToggler = document.getElementById("cart-close");
const cart = document.getElementById("m-cart");

const cartCheckoutDiv = cart.querySelector("div.checkout-btn");
const cartCheckoutButton = cartCheckoutDiv.querySelector("button");
cartCheckoutButton.disabled = true;
const cartCheckoutURL = cartCheckoutDiv.querySelector("a").href;

const addToCartButtons = document.querySelectorAll("span.btn-add-cart");

const SESSION_CART_NUM_PRODUCTS = "numProducts";
const SESSION_CART_PRODUCT_COUNT = "cartProductCount"; // index comes here
const SESSION_CART_PRODUCT_NAME = "cartProductName"; // index comes here
const SESSION_CART_PRODUCT_PRICE = "cartProductPrice"; // index comes here
const SESSION_CART_PRODUCT_IMG = "cartProductImg"; // index comes here
const SESSION_CART_PRODUCT_HANDLE = "cartProductHandle"; // index comes here

class Product {
	constructor(
		id = 0,
		handle = "",
		name = "",
		img = "",
		price = 0,                                                     
		count = 0,
		elem = null
	) {
		this.id = id;
		this.handle = handle;
		this.name = name;
		this.img = img;
		this.price = price;
		this.count = count;
		this.elem = elem;
	}
}

class Cart {
	/**
	 * @param {HTMLElement} cartElem
	 */
	constructor(cartElem) {
		/** @type {Product[]} */
		this.products = this.#retrieveProductsFromSessionStorage();
		this.cartElem = cartElem;

		this.renderCartElement();
	}

	#retrieveProductsFromSessionStorage() {
		const idToProductMap = new Map();

		for (const key in sessionStorage) {
			if (key.startsWith("cartProduct")) {
				const sessionProductId = parseInt(key.match(/\d+/)[0]);

				if (!idToProductMap.get(sessionProductId)) {
					idToProductMap.set(sessionProductId, new Product());
					idToProductMap.get(sessionProductId).id = sessionProductId;
				}

				const product = idToProductMap.get(sessionProductId);

				if (key.startsWith(SESSION_CART_PRODUCT_COUNT)) {
					product.count = parseInt(
						sessionStorage.getItem(
							SESSION_CART_PRODUCT_COUNT + product.id
						)
					);
				} else if (key.startsWith(SESSION_CART_PRODUCT_IMG)) {
					product.img = sessionStorage.getItem(
						SESSION_CART_PRODUCT_IMG + product.id
					);
				} else if (key.startsWith(SESSION_CART_PRODUCT_NAME)) {
					product.name = sessionStorage.getItem(
						SESSION_CART_PRODUCT_NAME + product.id
					);
				} else if (key.startsWith(SESSION_CART_PRODUCT_PRICE)) {
					product.price = parseFloat(
						sessionStorage.getItem(
							SESSION_CART_PRODUCT_PRICE + product.id
						)
					);
				} else if (key.startsWith(SESSION_CART_PRODUCT_HANDLE)) {
					product.handle = sessionStorage.getItem(
						SESSION_CART_PRODUCT_HANDLE + product.id
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

	clearCart() {
		this.products = [];
		sessionStorage.clear();
		this.renderCartElement();
	}

	/**
	 * @param {Element} productElem
	 */
	addToCart(productElem) {
		// @ts-ignore
		const productId = parseInt(productElem.dataset.productId);

		const productInList = this.products.find(
			(productInList) => productInList.id === productId
		);

		if (productInList) {
			productInList.count++;
		} else {
			const product = new Product(
				productId,
				productElem
					.querySelector("div.p-item-img a")
					// @ts-ignore
					.href.match(/product\/(.+)$/)[1],
				productElem.querySelector("h4.p-item-name a").textContent,
				productElem
					.querySelector("img")
					.src.replace("http://localhost:5000", ""),
				parseFloat(
					productElem
						.querySelector("div.p-item-price span")
						.textContent.match(/\d+/)[0]
				),
				1,
				productElem
			);

			this.products.push(product);
		}

		this.#updateSessionStorage();
		this.renderCartElement();
	}

	#updateSessionStorage() {
		sessionStorage.clear();
		this.products.forEach((product) => {
			sessionStorage.setItem(
				SESSION_CART_PRODUCT_COUNT + product.id,
				"" + product.count
			);
			sessionStorage.setItem(
				SESSION_CART_PRODUCT_NAME + product.id,
				product.name
			);
			sessionStorage.setItem(
				SESSION_CART_PRODUCT_PRICE + product.id,
				"" + product.price
			);
			sessionStorage.setItem(
				SESSION_CART_PRODUCT_IMG + product.id,
				"" + product.img
			);
			sessionStorage.setItem(
				SESSION_CART_PRODUCT_HANDLE + product.id,
				"" + product.handle
			);
		});
	}

	/**
	 * @param { Product } product
	 */
	#buildCartProduct(product) {
		const cartProduct = document.createElement("div");
		cartProduct.classList.add("item");
		cartProduct.innerHTML = `
                <div class="image"><img src=${product.img} alt=${
			product.name
		} height="47"></div>
                <div class="info">
                    <div class="name">${product.name}</div>
                    <span class="amount">${product.price}</span>
                    <i class="material-icons">clear</i>
                    <span>${product.count}৳</span>
                    <span class="eq">=</span>
                    <span class="total">${product.price * product.count}৳</span>
                </div>
                <div class="remove" title="Remove"><i class="material-icons" aria-hidden="true">delete</i></div>
            `;

		cartProduct
			.querySelector("div.remove")
			.addEventListener(
				"click",
				this.removeCartElement.bind(this, product)
			);

		return cartProduct;
	}

	renderCartElement() {
		const cartContentDiv = this.cartElem.querySelector("div.content");
		cartContentDiv.replaceChildren();

		let total = 0.0;
		this.products.forEach((product) => {
			const cartProduct = this.#buildCartProduct(product);
			cartContentDiv.appendChild(cartProduct);
			total += product.count * product.price;
		});

		const cartSubtotal = document.querySelector("div.total div.amount");
		cartSubtotal.textContent = "" + total + "৳";

		cartToggler.title = `${this.products.length} item(s)`;
		const cartToggleCount = cartToggler.querySelector("span.counter");
		// @ts-ignore
		cartToggleCount.dataset.count = this.products.length;
		cartToggleCount.textContent = "" + this.products.length;

		cartCheckoutButton.disabled = this.products.length == 0;
	}

	/**
	 * @param {Product} product
	 */
	removeCartElement(product) {
		const index = this.products.findIndex(
			(productInList) => productInList.id === product.id
		);
		this.products.splice(index, 1);

		this.#updateSessionStorage();
		this.renderCartElement();
	}
}

const cartJS = new Cart(cart);

cartToggler.onclick = function () {
	cartToggler.classList.toggle("close");
	cartCloseToggler.classList.toggle("close");
	cart.classList.toggle("open");
};

cartCloseToggler.onclick = function () {
	cartToggler.click();
};

addToCartButtons.forEach((button) => {
	// @ts-ignore
	button.onclick = function () {
		const productElem = button.closest("div.p-item");
		cartJS.addToCart(productElem);
	};
});

cartCheckoutButton.onclick = function () {};
