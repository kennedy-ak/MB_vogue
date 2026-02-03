// MB Vogue - Main JavaScript

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functions
    initializeImageGallery();
    initializeVariantSelectors();
    initializeAutoDismissAlerts();
});

// Image Gallery Function
function initializeImageGallery() {
    const thumbnails = document.querySelectorAll('.thumbnail-img');
    const mainImage = document.getElementById('mainImage');

    if (thumbnails.length > 0 && mainImage) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Update main image
                mainImage.src = this.src;

                // Update active state
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
}

// Variant Selector Function
function initializeVariantSelectors() {
    const colorSelect = document.getElementById('colorSelect');
    const sizeSelect = document.getElementById('sizeSelect');

    if (colorSelect && sizeSelect) {
        // Store available variants data
        const availableVariants = JSON.parse(
            document.querySelector('[data-variants]')?.getAttribute('data-variants') || '{}'
        );

        colorSelect.addEventListener('change', function() {
            const selectedColor = this.value;

            // Update available sizes based on selected color
            if (availableVariants[selectedColor]) {
                const availableSizes = Object.keys(availableVariants[selectedColor]);

                // Clear and repopulate size select
                sizeSelect.innerHTML = '';
                availableSizes.forEach(size => {
                    const option = document.createElement('option');
                    option.value = size;
                    option.textContent = size;
                    sizeSelect.appendChild(option);
                });
            }
        });
    }
}

// Auto-dismiss alerts after 5 seconds
function initializeAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        // Check if alert has data-auto-dismiss attribute
        if (alert.getAttribute('data-auto-dismiss') !== 'false') {
            setTimeout(function() {
                // Fade out effect
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';

                setTimeout(function() {
                    alert.remove();
                }, 500);
            }, 5000);
        }

        // Add close button functionality
        const closeButton = alert.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                alert.remove();
            });
        }
    });
}

// Update cart quantity
function updateCartQuantity(itemId, newQuantity) {
    const form = document.querySelector(`form[action*="${itemId}"]`);
    if (form) {
        const input = form.querySelector('input[type="number"]');
        if (input) {
            input.value = newQuantity;
            form.submit();
        }
    }
}

// Remove from cart with confirmation
function removeFromCart(itemId) {
    if (confirm('Are you sure you want to remove this item from your cart?')) {
        window.location.href = `/cart/remove/${itemId}/`;
    }
}

// Format currency
function formatCurrency(amount) {
    return '₦' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize search debounce
const searchInput = document.querySelector('input[name="q"]');
if (searchInput) {
    searchInput.addEventListener('input', debounce(function(e) {
        // Auto-submit search form after user stops typing
        const form = e.target.closest('form');
        if (form && e.target.value.length > 2) {
            form.submit();
        }
    }, 500));
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Add to cart animation
function addToCartAnimation(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Adding...';
    button.disabled = true;

    setTimeout(function() {
        button.innerHTML = '<i class="bi bi-check"></i> Added!';
        button.classList.remove('btn-primary');
        button.classList.add('btn-success');

        setTimeout(function() {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
            button.disabled = false;
        }, 2000);
    }, 1000);
}

// Stock availability check
function checkStockAvailability(variantId) {
    fetch(`/api/check-stock/${variantId}/`)
        .then(response => response.json())
        .then(data => {
            const stockBadge = document.getElementById('stock-badge');
            if (stockBadge) {
                if (data.available) {
                    stockBadge.innerHTML = `<span class="badge bg-success">In Stock (${data.stock} available)</span>`;
                } else {
                    stockBadge.innerHTML = `<span class="badge bg-danger">Out of Stock</span>`;
                }
            }
        })
        .catch(error => console.error('Error checking stock:', error));
}

// Newsletter subscription (if you add this feature later)
function subscribeNewsletter(email) {
    // Prevent default form submission
    event.preventDefault();

    // Add your newsletter subscription logic here
    console.log('Newsletter subscription for:', email);
}

// Print order function
function printOrder(orderNumber) {
    window.print();
}

console.log('MB Vogue - JavaScript initialized successfully');
