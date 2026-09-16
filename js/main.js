// =========================
// TAB SWITCHER
// =========================
function switchTab(tabName, el) {

  // Remove active class dari semua tombol
  document.querySelectorAll('.paket-tab-btn')
    .forEach(btn => btn.classList.remove('active'));

  // Tambahkan active ke tombol yang diklik
  el.classList.add('active');

  // Hide semua panel
  document.querySelectorAll('.paket-panel')
    .forEach(panel => panel.classList.remove('active'));

  // Show panel target
  const targetPanel = document.getElementById(`panel-${tabName}`);

  if (targetPanel) {
    targetPanel.classList.add('active');
  }

}

// =========================
// PROMO GALLERY
// =========================
function initPromoGallery() {

  const gallery = document.getElementById('promoGallery');

  if (!gallery) {
    return;
  }

  const track = gallery.querySelector('.promo-gallery-track');
  const slides = gallery.querySelectorAll('.promo-gallery-slide');
  const dotsWrap = gallery.parentElement.querySelector('.promo-gallery-dots');
  const controls = gallery.querySelectorAll('[data-gallery-direction]');
  let activeIndex = 0;
  let autoplay;

  const render = () => {
    track.style.transform = `translateX(-${activeIndex * 100}%)`;
    dotsWrap.querySelectorAll('.promo-gallery-dot').forEach((dot, index) => {
      dot.classList.toggle('active', index === activeIndex);
      dot.setAttribute('aria-current', index === activeIndex ? 'true' : 'false');
    });
  };

  const move = (direction) => {
    activeIndex = (activeIndex + direction + slides.length) % slides.length;
    render();
  };

  slides.forEach((slide, index) => {
    const dot = document.createElement('button');
    dot.type = 'button';
    dot.className = 'promo-gallery-dot';
    dot.setAttribute('aria-label', `Tampilkan promo ${index + 1}`);
    dot.addEventListener('click', () => {
      activeIndex = index;
      render();
    });
    dotsWrap.appendChild(dot);
  });

  controls.forEach((control) => {
    control.addEventListener('click', () => move(Number(control.dataset.galleryDirection)));
  });

  const stopAutoplay = () => clearInterval(autoplay);
  const startAutoplay = () => {
    stopAutoplay();
    autoplay = setInterval(() => move(1), 5000);
  };

  gallery.addEventListener('mouseenter', stopAutoplay);
  gallery.addEventListener('mouseleave', startAutoplay);
  gallery.addEventListener('focusin', stopAutoplay);
  gallery.addEventListener('focusout', startAutoplay);
  gallery.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') move(-1);
    if (event.key === 'ArrowRight') move(1);
  });

  render();
  startAutoplay();
}

document.addEventListener('DOMContentLoaded', initPromoGallery);

// =========================
// BIZ SPEED SWITCH
// =========================
function switchBizSpeed(speed, btn) {

  // Remove active button
  document.querySelectorAll('.biz-speed-btn')
    .forEach(b => b.classList.remove('active'));

  // Active current button
  btn.classList.add('active');

  // Update harga
  document.querySelectorAll('.biz-price')
    .forEach(el => {

      const val = el.getAttribute(`data-${speed}`);

      if (val) {

        const priceNum = el.querySelector('.biz-price-num');

        if (priceNum) {
          priceNum.textContent = val;
        }

      }

    });

}

// =========================
// FAQ TOGGLE
// =========================
function toggleFaq(btn) {

  const item = btn.parentElement;
  const answer = item.querySelector('.faq-a');
  const isOpen = btn.classList.contains('open');

  // Tutup semua FAQ
  document.querySelectorAll('.faq-q').forEach(q => {

    q.classList.remove('open');

    const parent = q.parentElement;

    parent.classList.remove('active');

    const ans = parent.querySelector('.faq-a');

    if (ans) {
      ans.classList.remove('open');
    }

  });

  // Buka FAQ yang diklik
  if (!isOpen) {

    btn.classList.add('open');

    item.classList.add('active');

    if (answer) {
      answer.classList.add('open');
    }

  }

}

// =========================
// LOCATION MODAL
// =========================
function openLocationModal() {

  const modal = document.getElementById('locationModal');

  if (modal) {
    modal.classList.add('show');
  }

}

function closeLocationModal() {

  const modal = document.getElementById('locationModal');

  if (modal) {
    modal.classList.remove('show');
  }

}

// =========================
// GET USER LOCATION
// =========================
async function getLocation() {

  const status = document.getElementById('locationStatus');
  const coord = document.getElementById('locationCoord');
  const waBtn = document.getElementById('waCoverageBtn');
  const coverageMap = document.getElementById('coverageMap');

  if (!navigator.geolocation) {

    alert('Browser tidak mendukung GPS.');
    return;

  }

  // Loading state
  status.innerHTML = `
    <i class="ti ti-loader-2"></i>
    Mengambil lokasi...
  `;

  coord.innerHTML = '';

  navigator.geolocation.getCurrentPosition(

    // SUCCESS
    async (position) => {

      const lat = position.coords.latitude;
      const lng = position.coords.longitude;

      // Update Google Maps
      if (coverageMap) {

        coverageMap.src =
          `https://maps.google.com/maps?q=${lat},${lng}&z=15&output=embed`;

      }

      let address = 'Lokasi berhasil didapat';

      // Reverse Geocoding
      try {

        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
          {
            headers: {
              'Accept': 'application/json'
            }
          }
        );

        const data = await response.json();

        if (data.display_name) {
          address = data.display_name;
        }

      } catch (error) {

        console.log('Gagal reverse geocoding:', error);

      }

      // Success UI
      status.innerHTML = `
        <i class="ti ti-circle-check"></i>
        Lokasi berhasil diambil
      `;

      coord.innerHTML = `
        ${address}
        <br><br>

        <strong>Latitude:</strong> ${lat}
        <br>

        <strong>Longitude:</strong> ${lng}
      `;

      // WhatsApp message
      const message =
`Halo ICONNET, saya ingin cek coverage dan pemasangan.

📍 Lokasi Saya:
${address}

📌 Google Maps:
https://www.google.com/maps?q=${lat},${lng}

Latitude: ${lat}
Longitude: ${lng}`;

      const waLink =
        `https://wa.me/6281339646353?text=${encodeURIComponent(message)}`;

      // Update tombol WA
      if (waBtn) {

        waBtn.href = waLink;

        waBtn.classList.remove('disabled');

      }

      // =========================
      // MODAL DATA
      // =========================
      const modalAddress = document.getElementById('modalAddress');
      const modalLat = document.getElementById('modalLat');
      const modalLng = document.getElementById('modalLng');
      const modalWaBtn = document.getElementById('modalWaBtn');

      if (modalAddress) {
        modalAddress.innerText = address;
      }

      if (modalLat) {
        modalLat.innerText = lat;
      }

      if (modalLng) {
        modalLng.innerText = lng;
      }

      if (modalWaBtn) {
        modalWaBtn.href = waLink;
      }

      // Open modal
      openLocationModal();

    },

    // ERROR
    (error) => {

      console.log(error);

      status.innerHTML = `
        <i class="ti ti-alert-circle"></i>
        Gagal mengambil lokasi
      `;

      coord.innerHTML =
        'Pastikan GPS dan izin lokasi browser aktif.';

    },

    // OPTIONS
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }

  );

}

// =========================
// NAVBAR SCROLL EFFECT
// =========================
const backToTop = document.getElementById('backToTop');

const updateScrollControls = () => {
  const navbar = document.getElementById('navbar');

  if (navbar) {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  }

  if (backToTop) {
    backToTop.classList.toggle('show', window.scrollY > 160);
  }
};

window.addEventListener('scroll', updateScrollControls, { passive: true });
updateScrollControls();

if (backToTop) {
  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// =========================
// MOBILE MENU
// =========================
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');

if (hamburger && navLinks) {

  hamburger.addEventListener('click', () => {

    navLinks.classList.toggle('open');

    const icon = hamburger.querySelector('i');

    if (icon) {

      if (navLinks.classList.contains('open')) {

        icon.className = 'ti ti-x';

      } else {

        icon.className = 'ti ti-menu-2';

      }

    }

  });

  // Close menu saat klik link
  navLinks.querySelectorAll('a').forEach(link => {

    link.addEventListener('click', () => {

      navLinks.classList.remove('open');

      const icon = hamburger.querySelector('i');

      if (icon) {
        icon.className = 'ti ti-menu-2';
      }

    });

  });

  // Close menu saat klik luar
  document.addEventListener('click', (e) => {

    if (
      !hamburger.contains(e.target) &&
      !navLinks.contains(e.target)
    ) {

      navLinks.classList.remove('open');

      const icon = hamburger.querySelector('i');

      if (icon) {
        icon.className = 'ti ti-menu-2';
      }

    }

  });

}

// =========================
// CLOSE MODAL CLICK OUTSIDE
// =========================
window.addEventListener('click', (e) => {

  const modal = document.getElementById('locationModal');

  if (e.target === modal) {
    closeLocationModal();
  }

});