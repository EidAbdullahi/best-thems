// ==========================================================================
// EAGLE SECURITY - ADMIN DASHBOARD JAVASCRIPT
// ==========================================================================

// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('adminSidebar');
    const toggle = document.getElementById('sidebarToggle');
    if (window.innerWidth <= 768 && 
        sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
    }
});

// ===== STATUS TOGGLE AJAX =====
document.querySelectorAll('.status-toggle').forEach(btn => {
    btn.addEventListener('click', async function() {
        const url = this.dataset.url;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const data = await response.json();

            if (data.status === 'success') {
                this.classList.toggle('active', data.is_active);
            }
        } catch (err) {
            console.error('Toggle failed:', err);
        }
    });
});

// ===== CSRF TOKEN HELPER =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===== AUTO-DISMISS TOASTS =====
document.querySelectorAll('.toast').forEach(toast => {
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 400);
    }, 5000);
});

// ===== CONFIRM DELETE =====
document.querySelectorAll('.confirm-delete').forEach(btn => {
    btn.addEventListener('click', function(e) {
        if (!confirm(this.dataset.confirm || 'Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
});

// ===== IMAGE PREVIEW ON FILE SELECT =====
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function() {
        const preview = document.getElementById(this.dataset.preview);
        if (preview && this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => { preview.src = e.target.result; };
            reader.readAsDataURL(this.files[0]);
        }
    });
});

// ===== SEARCH DEBOUNCE =====
const searchInputs = document.querySelectorAll('.search-input');
searchInputs.forEach(input => {
    let timeout;
    input.addEventListener('input', function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            this.closest('form').submit();
        }, 500);
    });
});