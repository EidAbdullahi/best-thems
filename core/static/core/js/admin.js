// ==========================================================================
// EAGLE SECURITY — MODERN ADMIN DASHBOARD JAVASCRIPT
// Mobile-first · Accessible · Performance-optimized
// ==========================================================================

(function() {
    "use strict";

    // ===== CONFIGURATION =====
    const CONFIG = {
        SIDEBAR_BREAKPOINT: 1024,
        TOAST_DURATION: 5000,
        SEARCH_DEBOUNCE: 400,
        SWIPE_THRESHOLD: 50,
    };

    // ===== UTILITIES =====
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
    const debounce = (fn, ms) => {
        let t;
        return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
    };
    const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // ===== CSRF TOKEN =====
    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()[\]\\/+^])/g, "\\$1") + "=([^;]*)"));
        return match ? decodeURIComponent(match[1]) : null;
    }

    // ===== SIDEBAR =====
    function initSidebar() {
        const sidebar = $("#adminSidebar");
        const toggle = $("#sidebarToggle");
        if (!sidebar || !toggle) return;

        let overlay = $(".sidebar-overlay");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.className = "sidebar-overlay";
            overlay.setAttribute("aria-hidden", "true");
            document.body.appendChild(overlay);
        }

        function openSidebar() {
            sidebar.classList.add("open");
            toggle.setAttribute("aria-expanded", "true");
            overlay.classList.add("active");
            document.body.style.overflow = "hidden";
            const firstNav = $(".nav-item", sidebar);
            if (firstNav) firstNav.focus();
        }

        function closeSidebar() {
            sidebar.classList.remove("open");
            toggle.setAttribute("aria-expanded", "false");
            overlay.classList.remove("active");
            document.body.style.overflow = "";
            toggle.focus();
        }

        function toggleSidebar() {
            if (sidebar.classList.contains("open")) closeSidebar();
            else openSidebar();
        }

        toggle.addEventListener("click", toggleSidebar);
        overlay.addEventListener("click", closeSidebar);

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && sidebar.classList.contains("open")) {
                closeSidebar();
            }
        });

        let touchStartX = 0;
        sidebar.addEventListener("touchstart", (e) => {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });

        sidebar.addEventListener("touchend", (e) => {
            const diff = e.changedTouches[0].clientX - touchStartX;
            if (diff < -CONFIG.SWIPE_THRESHOLD) closeSidebar();
        }, { passive: true });

        const mql = window.matchMedia(`(min-width: ${CONFIG.SIDEBAR_BREAKPOINT}px)`);
        const handleBreakpoint = (e) => {
            if (e.matches && sidebar.classList.contains("open")) {
                closeSidebar();
            }
        };
        mql.addEventListener("change", handleBreakpoint);
        handleBreakpoint(mql);
    }

    // ===== STATUS TOGGLE (AJAX) =====
    function initStatusToggles() {
        $$(".status-toggle").forEach((btn) => {
            btn.addEventListener("click", async function() {
                const url = this.dataset.url;
                if (!url) return;

                const wasActive = this.classList.contains("active");
                this.classList.toggle("active");
                this.setAttribute("aria-pressed", String(!wasActive));
                this.disabled = true;

                try {
                    const response = await fetch(url, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCookie("csrftoken") || "",
                            "X-Requested-With": "XMLHttpRequest",
                            "Content-Type": "application/json",
                        },
                        credentials: "same-origin",
                    });

                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const data = await response.json();

                    if (data.status !== "success") {
                        this.classList.toggle("active", wasActive);
                        this.setAttribute("aria-pressed", String(wasActive));
                        showToast("Failed to update status", "error");
                    } else {
                        this.classList.toggle("active", !!data.is_active);
                        this.setAttribute("aria-pressed", String(!!data.is_active));
                    }
                } catch (err) {
                    this.classList.toggle("active", wasActive);
                    this.setAttribute("aria-pressed", String(wasActive));
                    showToast("Network error. Please try again.", "error");
                    console.error("Toggle failed:", err);
                } finally {
                    this.disabled = false;
                }
            });
        });
    }

    // ===== TOAST NOTIFICATIONS =====
    function showToast(message, type = "info") {
        let container = $(".toast-container");
        if (!container) {
            container = document.createElement("div");
            container.className = "toast-container";
            container.setAttribute("role", "region");
            container.setAttribute("aria-live", "polite");
            container.setAttribute("aria-label", "Notifications");
            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.setAttribute("role", "status");
        toast.innerHTML = `
            <span>${escapeHtml(message)}</span>
            <button type="button" aria-label="Dismiss notification">&times;</button>
        `;

        container.appendChild(toast);

        const timer = setTimeout(() => dismissToast(toast), CONFIG.TOAST_DURATION);

        toast.querySelector("button").addEventListener("click", () => {
            clearTimeout(timer);
            dismissToast(toast);
        });

        toast.addEventListener("mouseenter", () => clearTimeout(timer));
        toast.addEventListener("mouseleave", () => setTimeout(() => dismissToast(toast), CONFIG.TOAST_DURATION));
    }

    function dismissToast(toast) {
        if (!toast || !toast.parentNode) return;
        toast.style.animation = "toastFadeOut 0.3s ease forwards";
        setTimeout(() => toast.remove(), 300);
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    // ===== CONFIRM DELETE =====
    function initConfirmDelete() {
        document.addEventListener("click", (e) => {
            const btn = e.target.closest(".confirm-delete");
            if (!btn) return;
            const msg = btn.dataset.confirm || "Are you sure you want to delete this item?";
            if (!confirm(msg)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    }

    // ===== IMAGE PREVIEW =====
    function initImagePreviews() {
        $$("input[type=\"file\"][data-preview]").forEach((input) => {
            input.addEventListener("change", function() {
                const preview = $(`#${this.dataset.preview}`);
                if (!preview || !this.files || !this.files[0]) return;

                if (!this.files[0].type.startsWith("image/")) {
                    showToast("Please select a valid image file", "warning");
                    this.value = "";
                    return;
                }

                const reader = new FileReader();
                reader.onload = (e) => { preview.src = e.target.result; };
                reader.readAsDataURL(this.files[0]);
            });
        });
    }

    // ===== SEARCH DEBOUNCE =====
    function initSearchDebounce() {
        $$(".search-input").forEach((input) => {
            const form = input.closest("form");
            if (!form) return;

            const debouncedSubmit = debounce(() => form.submit(), CONFIG.SEARCH_DEBOUNCE);
            input.addEventListener("input", debouncedSubmit);
        });
    }

    // ===== CHART INITIALIZATION =====
    function initChart() {
        const canvas = $("#trendChart");
        if (!canvas || typeof Chart === "undefined") return;

        const wrap = canvas.parentElement;
        if (wrap && wrap.offsetHeight < 50) {
            wrap.style.height = "260px";
        }

        // Read chart data from JSON script tags
        let labels = [];
        let data = [];

        const labelsScript = $("#chart-data");
        const valuesScript = $("#chart-values");

        if (labelsScript && valuesScript) {
            try {
                labels = JSON.parse(labelsScript.textContent.trim());
                data = JSON.parse(valuesScript.textContent.trim());
            } catch (e) {
                console.warn("Chart data parse error:", e);
                return;
            }
        }

        if (!labels.length || !data.length) {
            console.warn("Chart data empty — labels or data array is empty");
            return;
        }

        document.fonts.ready.then(() => {
            const ctx = canvas.getContext("2d");

            new Chart(ctx, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Inquiries",
                        data: data,
                        borderColor: "#D4AF37",
                        backgroundColor: (ctx) => {
                            const chart = ctx.chart;
                            const { ctx: c, chartArea } = chart;
                            if (!chartArea) return null;
                            const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                            gradient.addColorStop(0, "rgba(212,175,55,0.15)");
                            gradient.addColorStop(1, "rgba(212,175,55,0)");
                            return gradient;
                        },
                        borderWidth: 2.5,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: "#0A0F1A",
                        pointBorderColor: "#D4AF37",
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 7,
                        pointHitRadius: 12,
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { intersect: false, mode: "index" },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: "rgba(10,15,26,0.95)",
                            titleColor: "#D4AF37",
                            bodyColor: "#E8ECF1",
                            borderColor: "rgba(212,175,55,0.2)",
                            borderWidth: 1,
                            padding: 12,
                            cornerRadius: 10,
                            displayColors: false,
                            titleFont: { family: "Space Grotesk", size: 13 },
                            bodyFont: { family: "DM Sans", size: 12 },
                        },
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: "#5A6270",
                                font: { family: "JetBrains Mono", size: 11 },
                                maxRotation: 0,
                                autoSkip: true,
                                maxTicksLimit: 7,
                            },
                            border: { display: false },
                        },
                        y: {
                            grid: { color: "rgba(255,255,255,0.03)" },
                            ticks: {
                                color: "#5A6270",
                                font: { family: "JetBrains Mono", size: 11 },
                                stepSize: 1,
                                padding: 10,
                            },
                            border: { display: false },
                            beginAtZero: true,
                        },
                    },
                    animation: {
                        duration: prefersReducedMotion() ? 0 : 1000,
                        easing: "easeOutQuart",
                    },
                },
            });
        });
    }

    // ===== SECTOR BARS ANIMATION =====
    function initSectorBars() {
        const bars = $$(".dash-sector-bar");
        if (!bars.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const targetWidth = bar.style.width;
                    bar.style.width = "0%";
                    requestAnimationFrame(() => {
                        bar.style.width = targetWidth;
                    });
                    observer.unobserve(bar);
                }
            });
        }, { threshold: 0.2 });

        bars.forEach((bar) => observer.observe(bar));
    }

    // ===== ACTIVE NAV HIGHLIGHT =====
    function initActiveNav() {
        const currentPath = window.location.pathname;
        $$(".nav-item").forEach((item) => {
            const href = item.getAttribute("href");
            if (href && currentPath.startsWith(href) && href !== "/") {
                item.classList.add("active");
            }
        });
    }

    // ===== INIT =====
    function init() {
        initSidebar();
        initStatusToggles();
        initConfirmDelete();
        initImagePreviews();
        initSearchDebounce();
        initChart();
        initSectorBars();
        initActiveNav();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    window.getCookie = getCookie;
    window.showToast = showToast;
})();