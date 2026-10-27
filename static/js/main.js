/**
 * ENVITA — Climate Health Platform
 * Main JavaScript
 */

'use strict';

/* ============================================================
   DOM-Ready init
============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  initRadioCards();
  initCheckboxCards();
  initScoreAnimation();
  initAQIBar();
  initAutoHideAlerts();
  initLocationPlaceholder();
});


/* ============================================================
   Radio Card Highlight
============================================================ */
function initRadioCards() {
  document.querySelectorAll('.radio-card input[type="radio"]').forEach(input => {
    input.addEventListener('change', () => {
      const group = input.closest('.radio-card-group');
      if (!group) return;
      group.querySelectorAll('.radio-card').forEach(c => c.classList.remove('selected'));
      input.closest('.radio-card').classList.add('selected');
    });
  });
}


/* ============================================================
   Checkbox Card Highlight + "None" logic
============================================================ */
function initCheckboxCards() {
  const noneInput = document.querySelector('input[name="sensitivities"][value="None"]');
  const otherInputs = Array.from(
    document.querySelectorAll('input[name="sensitivities"]:not([value="None"])')
  );

  if (!noneInput) return;

  noneInput.addEventListener('change', () => {
    if (noneInput.checked) {
      otherInputs.forEach(cb => {
        cb.checked = false;
        _updateCheckboxCard(cb);
      });
    }
    _updateCheckboxCard(noneInput);
  });

  otherInputs.forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked) {
        noneInput.checked = false;
        _updateCheckboxCard(noneInput);
      }
      _updateCheckboxCard(cb);
    });
  });
}

function _updateCheckboxCard(input) {
  const card = input.closest('.checkbox-card');
  if (!card) return;
  const icon = card.querySelector('.check-icon');
  if (input.checked) {
    card.style.borderColor = 'var(--green-primary)';
    card.style.background  = 'var(--green-accent)';
    if (icon) icon.style.opacity = '1';
  } else {
    card.style.borderColor = '';
    card.style.background  = '';
    if (icon) icon.style.opacity = '0';
  }
}


/* ============================================================
   Score Circle Animation
   Triggers a CSS transition by setting the dasharray after load
============================================================ */
function initScoreAnimation() {
  const circles = document.querySelectorAll('.score-fill');
  circles.forEach(circle => {
    // Get target from existing stroke-dasharray attribute
    const target = parseFloat(circle.getAttribute('stroke-dasharray'));
    if (isNaN(target)) return;

    // Start at 0, animate to target
    circle.setAttribute('stroke-dasharray', `0 263.9`);
    requestAnimationFrame(() => {
      setTimeout(() => {
        circle.style.transition = 'stroke-dasharray 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
        circle.setAttribute('stroke-dasharray', `${target} 263.9`);
      }, 200);
    });
  });
}


/* ============================================================
   AQI Bar Animation
============================================================ */
function initAQIBar() {
  const fill = document.querySelector('.aqi-bar-fill');
  if (!fill) return;
  const targetWidth = fill.style.width;
  fill.style.width = '0%';
  setTimeout(() => {
    fill.style.transition = 'width 1s ease';
    fill.style.width = targetWidth;
  }, 300);
}


/* ============================================================
   Auto-dismiss flash alerts after 6 seconds
============================================================ */
function initAutoHideAlerts() {
  const alerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert?.close();
    }, 6000);
  });
}


/* ============================================================
   Location placeholder rotation (dashboard)
============================================================ */
function initLocationPlaceholder() {
  const input = document.querySelector('input[name="location"]');
  if (!input || input.value) return;

  const cities = [
    'London, UK',
    'New York, US',
    'Karachi, Pakistan',
    'Lagos, Nigeria',
    'Jakarta, Indonesia',
    'Delhi, India',
    'São Paulo, Brazil',
    'Cairo, Egypt',
  ];

  let i = 0;
  setInterval(() => {
    i = (i + 1) % cities.length;
    input.setAttribute('placeholder', `e.g. ${cities[i]}`);
  }, 3000);
}


/* ============================================================
   Loading state for forms
============================================================ */
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', () => {
    const btn = form.querySelector('button[type="submit"]');
    if (!btn) return;

    // Don't double-trigger if already loading
    if (btn.disabled) return;

    const originalHTML = btn.innerHTML;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading…`;
    btn.disabled = true;

    // Re-enable after 30s as a safety net
    setTimeout(() => {
      btn.innerHTML = originalHTML;
      btn.disabled = false;
    }, 30000);
  });
});
