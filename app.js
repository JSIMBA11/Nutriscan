const byId = (id) => document.getElementById(id);

async function scanBarcode() {
  const code = byId('barcode').value.trim();
  if (!code) return;
  const r = await fetch(`/api/scan/${code}`);
  const d = await r.json();
  byId('foodResult').textContent = JSON.stringify(d, null, 2);
}

async function searchFood() {
  const query = byId("query").value.trim();
  if (!query) return;

  // Use the correct API endpoint for food search
  const res = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
  if (!res.ok) {
    byId("foodResult").textContent = "Error: Unable to fetch food data.";
    return;
  }

  const data = await res.json();
  // Display results in a user-friendly way if possible
  if (Array.isArray(data) && data.length > 0) {
    byId("foodResult").innerHTML = data.map(item =>
      `<div><strong>${item.name || item.title || 'Item'}</strong><br>${item.description || ''}</div>`
    ).join('');
  } else if (typeof data === 'object' && data !== null) {
    byId("foodResult").textContent = JSON.stringify(data, null, 2);
  } else {
    byId("foodResult").textContent = "No results found.";
  }
}

async function addPantry() {
  const name = byId('pantryName').value.trim();
  const quantity = parseFloat(byId('pantryQty').value || '1');
  if (!name) return;
  await fetch('/api/pantry', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, quantity })
  });
  byId('pantryName').value = '';
  loadPantry();
}

async function loadPantry() {
  const r = await fetch('/api/pantry');
  const arr = await r.json();
  const ul = byId('pantryList');
  ul.innerHTML = '';
  arr.forEach(it => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${it.name} × ${it.quantity}</span> <button data-id="${it.id}">Remove</button>`;
    li.querySelector('button').onclick = async () => {
      await fetch(`/api/pantry/${it.id}`, { method: 'DELETE' });
      loadPantry();
    };
    ul.appendChild(li);
  });
}

async function getRecipes() {
  const goal = byId('goal').value;
  const r = await fetch('/api/pantry');
  const items = await r.json();
  const pantry = items.map(i => i.name);
  const resp = await fetch('/api/recipes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pantry, goal })
  });
  const data = await resp.json();
  const grid = byId('recipes');
  grid.innerHTML = '';
  data.forEach(rec => {
    const c = document.createElement('div');
    c.className = 'card recipe';
    c.innerHTML = `<h4>${rec.name || rec.title || 'Recipe'}</h4>
      <strong>Ingredients:</strong>
      <div>${(rec.ingredients || rec.needs || []).join(', ')}</div>
      <strong>Instructions:</strong>
      <div>${rec.instructions || (rec.steps ? rec.steps.join(' ') : '')}</div>`;
    grid.appendChild(c);
  });
}

// Map + donations
let map, userLatLng;
let mapInitialized = false;

function initMap() {
  if (mapInitialized) return;
  map = L.map('map').setView([0.0236, 37.9062], 6); // Kenya-ish default
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
  loadDonations();
  mapInitialized = true;
}

async function loadDonations() {
  const r = await fetch('/api/donations');
  const arr = await r.json();
  arr.forEach(d => {
    L.marker([d.lat, d.lng]).addTo(map).bindPopup(`<b>${d.item}</b> × ${d.quantity}<br/>By ${d.user_name}<br/>${d.note}`);
  });
}

function enableLocate() {
  if (!navigator.geolocation) return alert('Geolocation not supported');
  navigator.geolocation.getCurrentPosition(pos => {
    userLatLng = [pos.coords.latitude, pos.coords.longitude];
    map.setView(userLatLng, 13);
    L.marker(userLatLng).addTo(map).bindPopup('Your location');
  });
}

async function postDonation() {
  const payload = {
    user_name: byId('dName').value,
    item: byId('dItem').value,
    quantity: byId('dQty').value,
    note: byId('dNote').value,
    lat: userLatLng ? userLatLng[0] : 0,
    lng: userLatLng ? userLatLng[1] : 0,
  };
  await fetch('/api/donations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  alert('Donation posted!');
  map.eachLayer(function (layer) {
    if (layer instanceof L.Marker)
      map.removeLayer(layer);
  });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
  loadDonations();
}

// Lessons
async function loadLessons() {
  const r = await fetch('/api/lessons');
  const arr = await r.json();
  const box = byId('lessons');
  box.innerHTML = '';
  arr.forEach(ls => {
    const c = document.createElement('div');
    c.className = 'card';
    c.innerHTML = `<h4>${ls.title}</h4><p>${ls.content}</p>`;
    box.appendChild(c);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  loadPantry();
  loadLessons();
  // Do not initialize the map here
});

// Only initialize the map when the donate section is shown
const donateSectionBtn = document.getElementById('showDonateSection');
if (donateSectionBtn) {
  donateSectionBtn.addEventListener('click', () => {
    initMap();
    // Optionally, show the donate section here if it's hidden by default
    const donateSection = document.getElementById('donateSection');
    if (donateSection) donateSection.style.display = 'block';
  });
}


async function donate() {
  const res = await fetch("/create-checkout-session", {
    method: "POST",
  });
  const data = await res.json();

  const stripe = Stripe("YOUR_STRIPE_PUBLISHABLE_KEY"); // from dashboard
  stripe.redirectToCheckout({ sessionId: data.id });
}
