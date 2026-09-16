
document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================
       BOOTSTRAP TOOLTIPS
    =========================================== */

    const tooltipTriggerList = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
    );

    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });


    /* ==========================================
       BOOTSTRAP POPOVERS
    =========================================== */

    const popoverTriggerList = document.querySelectorAll(
        '[data-bs-toggle="popover"]'
    );

    popoverTriggerList.forEach(function (popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });


    /* ==========================================
       AUTO HIDE DJANGO MESSAGES
    =========================================== */

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            if (typeof bootstrap !== "undefined") {

                const alertInstance =
                    bootstrap.Alert.getOrCreateInstance(alert);

                alertInstance.close();

            } else {

                alert.remove();

            }

        }, 5000);

    });


    /* ==========================================
       NAVBAR ACTIVE LINK
    =========================================== */

    const currentPath = window.location.pathname;

    const navLinks = document.querySelectorAll(
        ".navbar-nav .nav-link"
    );

    navLinks.forEach(function (link) {

        const href = link.getAttribute("href");

        if (!href || href === "#") {
            return;
        }

        if (href === currentPath) {

            link.classList.add("active");

        }

    });


    /* ==========================================
       SMOOTH SCROLL
    =========================================== */

    const smoothScrollLinks = document.querySelectorAll(
        'a[href^="#"]'
    );

    smoothScrollLinks.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId =
                this.getAttribute("href");

            if (
                !targetId ||
                targetId === "#"
            ) {
                return;
            }

            const target =
                document.querySelector(targetId);

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        });

    });


    /* ==========================================
       BACK TO TOP BUTTON
    =========================================== */

    let backToTopButton =
        document.getElementById("backToTop");

    if (backToTopButton) {

        window.addEventListener("scroll", function () {

            if (window.scrollY > 300) {

                backToTopButton.style.display = "block";

            } else {

                backToTopButton.style.display = "none";

            }

        });


        backToTopButton.addEventListener(
            "click",
            function () {

                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

            }
        );

    }


    /* ==========================================
       PRODUCT IMAGE ERROR HANDLING
    =========================================== */

    const productImages =
        document.querySelectorAll("img");

    productImages.forEach(function (image) {

        image.addEventListener("error", function () {

            /*
             * Do not repeatedly trigger the error event.
             */

            if (
                this.dataset.imageErrorHandled === "true"
            ) {
                return;
            }

            this.dataset.imageErrorHandled = "true";

            /*
             * Hide broken image.
             */

            this.style.display = "none";

        });

    });


    /* ==========================================
       QUANTITY BUTTONS
    =========================================== */

    const quantityButtons =
        document.querySelectorAll(
            ".quantity-btn"
        );

    quantityButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const action =
                this.dataset.action;

            const input =
                this.closest(".quantity-control")
                    ?.querySelector(".quantity-input");

            if (!input) {
                return;
            }

            let quantity =
                parseInt(input.value) || 1;

            if (action === "increase") {

                quantity++;

            }

            if (action === "decrease") {

                quantity--;

                if (quantity < 1) {
                    quantity = 1;
                }

            }

            input.value = quantity;

        });

    });


    /* ==========================================
       PASSWORD SHOW / HIDE
    =========================================== */

    const passwordToggles =
        document.querySelectorAll(
            ".password-toggle"
        );

    passwordToggles.forEach(function (toggle) {

        toggle.addEventListener(
            "click",
            function () {

                const input =
                    document.querySelector(
                        this.dataset.target
                    );

                if (!input) {
                    return;
                }

                if (input.type === "password") {

                    input.type = "text";

                    this.classList.remove(
                        "fa-eye"
                    );

                    this.classList.add(
                        "fa-eye-slash"
                    );

                } else {

                    input.type = "password";

                    this.classList.remove(
                        "fa-eye-slash"
                    );

                    this.classList.add(
                        "fa-eye"
                    );

                }

            }
        );

    });


    /* ==========================================
       CONFIRM DELETE
    =========================================== */

    const deleteButtons =
        document.querySelectorAll(
            ".delete-confirm"
        );

    deleteButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                const message =
                    this.dataset.message ||
                    "Are you sure you want to delete this item?";

                if (!confirm(message)) {

                    event.preventDefault();

                }

            }
        );

    });


    /* ==========================================
       FORM SUBMIT PROTECTION
    =========================================== */

    const forms =
        document.querySelectorAll(
            "form"
        );

    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function () {

                const submitButtons =
                    form.querySelectorAll(
                        'button[type="submit"], input[type="submit"]'
                    );

                submitButtons.forEach(
                    function (button) {

                        /*
                         * Do not disable login/register buttons
                         * permanently if browser validation fails.
                         */

                        if (
                            form.checkValidity &&
                            !form.checkValidity()
                        ) {
                            return;
                        }

                        button.dataset.originalText =
                            button.innerHTML;

                        button.disabled = true;

                    }
                );

            }
        );

    });


    /* ==========================================
       SEARCH INPUT
    =========================================== */

    const searchInputs =
        document.querySelectorAll(
            ".search-input"
        );

    searchInputs.forEach(function (input) {

        input.addEventListener(
            "keypress",
            function (event) {

                if (event.key === "Enter") {

                    const searchValue =
                        this.value.trim();

                    if (searchValue !== "") {

                        const searchUrl =
                            this.dataset.searchUrl;

                        if (searchUrl) {

                            window.location.href =
                                searchUrl +
                                "?q=" +
                                encodeURIComponent(
                                    searchValue
                                );

                        }

                    }

                }

            }
        );

    });


    /* ==========================================
       CONSOLE MESSAGE
    =========================================== */

    console.log(
        "Vetri AI Ecommerce JavaScript loaded successfully."
    );

});

