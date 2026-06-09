const tg = window.Telegram?.WebApp;
let tripId = null;
let chatId = null;

function init() {
  if (tg) {
    tg.expand();
    tg.ready();
  }

  const params = new URLSearchParams(window.location.search);
  tripId = params.get('trip_id');
  chatId = params.get('chat_id') || tg?.initDataUnsafe?.chat_id;

  if (tripId) {
    loadItems();
  } else if (chatId) {
    loadTrips();
  } else {
    showEmpty('Нет данных. Откройте WebApp из бота.');
  }
}

async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.status === 204 ? null : res.json();
}

async function loadTrips() {
  try {
    const trips = await api('GET', `/api/trips?chat_id=${chatId}`);
    showTrips(trips);
  } catch (e) {
    showEmpty('Ошибка загрузки: ' + e.message);
  }
}

function showTrips(trips) {
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('trips-view').classList.remove('hidden');

  const container = document.getElementById('trips-list');
  container.innerHTML = '';

  if (trips.length === 0) {
    container.innerHTML = '<p style="text-align:center;color:var(--tg-theme-hint-color);padding:40px">Нет поездок</p>';
    return;
  }

  for (const t of trips) {
    const card = document.createElement('div');
    card.className = 'trip-card';
    card.innerHTML = `
      <div class="trip-name">${t.name}</div>
      <div class="trip-meta">${t.status} · ${new Date(t.created_at).toLocaleDateString()}</div>
    `;
    card.onclick = () => window.location.href = `/?trip_id=${t.id}&chat_id=${chatId}`;
    container.appendChild(card);
  }
}

async function loadItems() {
  try {
    const [trip, items] = await Promise.all([
      api('GET', `/api/trips/${tripId}`),
      api('GET', `/api/trips/${tripId}/items'),
    ]);
    showItems(trip, items);
  } catch (e) {
    showEmpty('Ошибка загрузки: ' + e.message);
  }
}

function showItems(trip, items) {
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('items-view').classList.remove('hidden');

  document.getElementById('trip-title').textContent = `🏕 ${trip.name}`;

  const container = document.getElementById('items-list');
  container.innerHTML = '';

  if (items.length === 0) {
    document.getElementById('empty-state').classList.remove('hidden');
  } else {
    document.getElementById('empty-state').classList.add('hidden');
  }

  for (const item of items) {
    const div = document.createElement('div');
    div.className = 'item' + (item.is_bought ? ' bought' : '');
    div.innerHTML = `
      <div class="checkbox">${item.is_bought ? '✓' : ''}</div>
      <div class="info">
        <div class="name">${item.name}</div>
        <div class="amount">${item.amount || ''}</div>
      </div>
      <button class="delete-btn" data-id="${item.id}">✕</button>
    `;
    const checkbox = div.querySelector('.checkbox');
    checkbox.onclick = () => toggleItem(item.id, div);

    const del = div.querySelector('.delete-btn');
    del.onclick = (e) => {
      e.stopPropagation();
      deleteItem(item.id, div);
    };

    container.appendChild(div);
  }

  if (tg) {
    tg.MainButton.setText('+ Добавить товар');
    tg.MainButton.show();
    tg.MainButton.onClick(showAddModal);
  }
}

async function toggleItem(id, el) {
  try {
    const res = await api('PATCH', `/api/items/${id}/toggle`);
    el.classList.toggle('bought', res.is_bought);
    el.querySelector('.checkbox').textContent = res.is_bought ? '✓' : '';
  } catch (e) {
    alert('Ошибка: ' + e.message);
  }
}

async function deleteItem(id, el) {
  try {
    await api('DELETE', `/api/items/${id}`);
    el.remove();
    const container = document.getElementById('items-list');
    if (container.children.length === 0) {
      document.getElementById('empty-state').classList.remove('hidden');
    }
  } catch (e) {
    alert('Ошибка: ' + e.message);
  }
}

function showAddModal() {
  document.getElementById('add-modal').classList.remove('hidden');
  document.getElementById('item-name').focus();
}

async function saveItem() {
  const name = document.getElementById('item-name').value.trim();
  const amount = document.getElementById('item-amount').value.trim();
  const category = document.getElementById('item-category').value;

  if (!name) return;

  try {
    await api('POST', `/api/trips/${tripId}/items`, { name, amount, category });
    document.getElementById('add-modal').classList.add('hidden');
    document.getElementById('item-name').value = '';
    document.getElementById('item-amount').value = '';
    loadItems();
  } catch (e) {
    alert('Ошибка: ' + e.message);
  }
}

function closeModal() {
  document.getElementById('add-modal').classList.add('hidden');
}

document.getElementById('save-item').onclick = saveItem;
document.getElementById('cancel-item').onclick = closeModal;

document.addEventListener('DOMContentLoaded', init);
