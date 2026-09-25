// State
let allFaculties = [];
let allDirections = [];
let searchDebounceTimer = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuth();
  setupNavigation();
  await loadInitialData();
  await switchTab('dashboard');
  setupForms();
});

// Toast notification
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : '⚠️'}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Auth Verification
async function checkAuth() {
  try {
    const res = await fetch('/api/v1/auth/me');
    if (!res.ok) throw new Error('Not authenticated');
    const admin = await res.json();
    document.getElementById('adminFullName').innerText = admin.full_name;
    document.getElementById('avatarLetter').innerText = admin.full_name.charAt(0).toUpperCase();
    if (admin.telegram_chat_id) {
      document.getElementById('telegramChatIdInput').value = admin.telegram_chat_id;
    }
  } catch (err) {
    window.location.href = '/login';
  }
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', async () => {
  try {
    await fetch('/api/v1/auth/logout', { method: 'POST' });
  } finally {
    localStorage.clear();
    window.location.href = '/login';
  }
});

// Navigation & Tab Switching
function setupNavigation() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const tabName = item.getAttribute('data-tab');
      switchTab(tabName);
    });
  });
}

async function switchTab(tabName) {
  // Update nav state
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.getAttribute('data-tab') === tabName);
  });

  // Update tab pane visibility
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.style.display = 'none';
  });

  const activePane = document.getElementById(`tab-${tabName}`);
  if (activePane) {
    activePane.style.display = 'block';
  }

  // Load relevant data for tab
  if (tabName === 'dashboard') {
    await loadDashboardStats();
  } else if (tabName === 'clubs') {
    await loadClubs();
  } else if (tabName === 'students') {
    await fetchStudents();
  } else if (tabName === 'academic') {
    await loadAcademicTables();
  } else if (tabName === 'settings') {
    await loadChannelSettings();
  }
}

// Initial Common Data (Faculties & Directions)
async function loadInitialData() {
  try {
    const [facRes, dirRes] = await Promise.all([
      fetch('/api/v1/faculties'),
      fetch('/api/v1/directions')
    ]);

    allFaculties = await facRes.json();
    allDirections = await dirRes.json();

    populateFacultyDropdowns();
  } catch (err) {
    console.error('Failed to load initial metadata:', err);
  }
}

function populateFacultyDropdowns() {
  const selects = ['clubFilterFaculty', 'studentFilterFaculty', 'directionFormFacultyId'];
  selects.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const isFilter = id.includes('Filter');
    el.innerHTML = isFilter ? '<option value="">Barcha fakultetlar</option>' : '<option value="">Fakultetni tanlang</option>';
    allFaculties.forEach(fac => {
      el.innerHTML += `<option value="${fac.id}">${fac.name}</option>`;
    });
  });

  // Populate direction dropdown in Club modal
  const clubDirSelect = document.getElementById('clubFormDirectionId');
  if (clubDirSelect) {
    clubDirSelect.innerHTML = '<option value="">Yo\'nalishni tanlang</option>';
    allDirections.forEach(dir => {
      clubDirSelect.innerHTML += `<option value="${dir.id}">${dir.faculty_name ? dir.faculty_name + ' -> ' : ''}${dir.name}</option>`;
    });
  }
}

// 1. DASHBOARD
async function loadDashboardStats() {
  try {
    const res = await fetch('/api/v1/stats/overview');
    const data = await res.json();

    document.getElementById('kpiStudents').innerText = data.students_count;
    document.getElementById('kpiClubs').innerText = data.clubs_count;
    document.getElementById('kpiFaculties').innerText = data.faculties_count;
    document.getElementById('kpiDirections').innerText = data.directions_count;

    // Top clubs
    const topClubsList = document.getElementById('topClubsList');
    if (data.top_clubs.length === 0) {
      topClubsList.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">Hozircha a\'zo bo\'lgan talabalar yo\'q.</p>';
    } else {
      topClubsList.innerHTML = data.top_clubs.map(c => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(11, 15, 25, 0.4); border-radius: var(--radius-md);">
          <span style="font-size: 13px; font-weight: 500;">🎯 ${c.name}</span>
          <span class="badge badge-indigo">${c.count} nafar talaba</span>
        </div>
      `).join('');
    }

    // Faculty breakdown
    const facList = document.getElementById('facultyBreakdownList');
    if (data.faculty_breakdown.length === 0) {
      facList.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">Ma\'lumotlar mavjud emas.</p>';
    } else {
      facList.innerHTML = data.faculty_breakdown.map(f => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(11, 15, 25, 0.4); border-radius: var(--radius-md);">
          <span style="font-size: 13px; font-weight: 500;">🏛 ${f.name}</span>
          <span class="badge badge-emerald">${f.count} nafar</span>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Error loading dashboard stats:', err);
  }
}

// 2. CLUBS MANAGEMENT
let currentClubs = [];

async function loadClubs() {
  const facId = document.getElementById('clubFilterFaculty').value;
  let url = '/api/v1/clubs';
  if (facId) url += `?faculty_id=${facId}`;

  try {
    const res = await fetch(url);
    currentClubs = await res.json();
    document.getElementById('clubsCountBadge').innerText = `${currentClubs.length} ta to'garak`;

    const grid = document.getElementById('clubsGrid');
    if (currentClubs.length === 0) {
      grid.innerHTML = '<p style="color: var(--text-muted); font-size: 13px; grid-column: 1/-1;">To\'garaklar topilmadi.</p>';
      return;
    }

    grid.innerHTML = currentClubs.map(c => `
      <div class="glass-panel club-card">
        <div>
          <div class="club-header">
            <div class="badge badge-indigo">${c.faculty_name || 'Fakultet'}</div>
            <div class="badge badge-emerald">${c.students_count} nafar a'zo</div>
          </div>
          <h3 class="club-title">${c.name}</h3>
          <p class="club-desc">${c.description}</p>
          <div class="club-meta-list">
            <div class="club-meta-item"><span>📚</span> <span><b>Yo'nalish:</b> ${c.direction_name || '-'}</span></div>
            <div class="club-meta-item"><span>🗓</span> <span><b>Kunlar:</b> ${c.schedule_days}</span></div>
            <div class="club-meta-item"><span>⏰</span> <span><b>Vaqt:</b> ${c.schedule_time}</span></div>
            <div class="club-meta-item"><span>📍</span> <span><b>Xona:</b> ${c.room_location}</span></div>
            <div class="club-meta-item"><span>👨‍🏫</span> <span><b>Rahbar:</b> ${c.leader_name}</span></div>
            <div class="club-meta-item"><span>📞</span> <span><b>Aloqa:</b> ${c.leader_contact}</span></div>
          </div>
        </div>
        <div class="club-footer">
          <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="editClub(${c.id})">
            ✏️ Tahrirlash
          </button>
          <button class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="deleteClub(${c.id})">
            🗑 O'chirish
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    showToast('To\'garaklarni yuklashda xatolik yuz berdi', 'error');
  }
}

function filterClubs() {
  loadClubs();
}

function openClubModal(clubData = null) {
  const modal = document.getElementById('clubModal');
  const form = document.getElementById('clubForm');
  form.reset();

  if (clubData) {
    document.getElementById('clubModalTitle').innerText = 'To\'garakni tahrirlash';
    document.getElementById('clubFormId').value = clubData.id;
    document.getElementById('clubFormDirectionId').value = clubData.direction_id;
    document.getElementById('clubFormName').value = clubData.name;
    document.getElementById('clubFormDesc').value = clubData.description;
    document.getElementById('clubFormDays').value = clubData.schedule_days;
    document.getElementById('clubFormTime').value = clubData.schedule_time;
    document.getElementById('clubFormRoom').value = clubData.room_location;
    document.getElementById('clubFormLeaderName').value = clubData.leader_name;
    document.getElementById('clubFormLeaderContact').value = clubData.leader_contact;
  } else {
    document.getElementById('clubModalTitle').innerText = 'Yangi to\'garak ochish';
    document.getElementById('clubFormId').value = '';
  }

  modal.classList.add('show');
}

function closeClubModal() {
  document.getElementById('clubModal').classList.remove('show');
}

function editClub(id) {
  const club = currentClubs.find(c => c.id === id);
  if (club) openClubModal(club);
}

async function deleteClub(id) {
  if (!confirm('Haqiqatdan ham ushbu to\'garakni o\'chirmoqchimisiz? Undagi talabalar a\'zoligi ham bekor qilinadi.')) return;
  try {
    const res = await fetch(`/api/v1/clubs/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast('To\'garak muvaffaqiyatli o\'chirildi');
    await loadClubs();
    await loadInitialData();
  } catch (err) {
    showToast('To\'garakni o\'chirishda xatolik yuz berdi', 'error');
  }
}

// 3. STUDENTS REGISTRATIONS
async function fetchStudents() {
  const facultyId = document.getElementById('studentFilterFaculty').value;
  const clubId = document.getElementById('studentFilterClub').value;
  const courseLevel = document.getElementById('studentFilterCourse').value;
  const search = document.getElementById('studentSearchInput').value.trim();

  let params = new URLSearchParams();
  if (facultyId) params.append('faculty_id', facultyId);
  if (clubId) params.append('club_id', clubId);
  if (courseLevel) params.append('course_level', courseLevel);
  if (search) params.append('search', search);

  // Update export links dynamically with query params
  document.getElementById('btnExportExcel').href = `/api/v1/export/excel?${params.toString()}`;
  document.getElementById('btnExportCsv').href = `/api/v1/export/csv?${params.toString()}`;

  try {
    const res = await fetch(`/api/v1/registrations?${params.toString()}`);
    const data = await res.json();

    const tbody = document.getElementById('studentsTableBody');
    if (!data.items || data.items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: var(--text-muted); padding: 32px;">A\'zo bo\'lgan talabalar topilmadi.</td></tr>';
      return;
    }

    tbody.innerHTML = data.items.map((item, idx) => {
      const regDate = new Date(item.registered_at).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
      const tgText = item.telegram_username ? `<a href="https://t.me/${item.telegram_username}" target="_blank" style="color: #818CF8; text-decoration: none;">@${item.telegram_username}</a>` : '<span style="color: var(--text-muted);">-</span>';

      return `
        <tr>
          <td><b>${idx + 1}</b></td>
          <td><b>${item.full_name}</b></td>
          <td>${item.faculty_name}</td>
          <td>${item.direction_name}</td>
          <td><span class="badge badge-indigo">${item.club_name}</span></td>
          <td><span class="badge badge-emerald">${item.course_level}-kurs</span></td>
          <td><a href="tel:${item.phone_number}" style="color: var(--text-primary); text-decoration: none;">${item.phone_number}</a></td>
          <td>${tgText}</td>
          <td style="font-size: 11px; color: var(--text-secondary);">${regDate}</td>
          <td>
            <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="deleteRegistration(${item.id})">
              Bekor qilish
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    showToast('Talabalar ro\'yxatini yuklashda xatolik yuz berdi', 'error');
  }
}

function debounceStudentSearch() {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    fetchStudents();
  }, 350);
}

function onStudentFacultyChange() {
  const facId = document.getElementById('studentFilterFaculty').value;
  const clubSelect = document.getElementById('studentFilterClub');
  clubSelect.innerHTML = '<option value="">Barcha to\'garaklar</option>';

  const filtered = facId ? currentClubs.filter(c => c.faculty_id == facId) : currentClubs;
  filtered.forEach(c => {
    clubSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
  });

  fetchStudents();
}

async function deleteRegistration(id) {
  if (!confirm('Ushbu talabaning to\'garakka a\'zoligini bekor qilmoqchimisiz?')) return;
  try {
    const res = await fetch(`/api/v1/registrations/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast('Talaba to\'garakdan muvaffaqiyatli chiqarildi');
    await fetchStudents();
  } catch (err) {
    showToast('A\'zolikni bekor qilishda xatolik yuz berdi', 'error');
  }
}

// 4. ACADEMIC TABLES
async function loadAcademicTables() {
  await loadInitialData();

  // Faculties Table
  const facBody = document.getElementById('facultiesTableBody');
  facBody.innerHTML = allFaculties.map(f => `
    <tr>
      <td><b>${f.name}</b> <span style="font-size: 11px; color: var(--text-muted);">${f.code || ''}</span></td>
      <td><span class="badge badge-indigo">${f.directions_count || 0} ta yo'nalish</span></td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="editFaculty(${f.id})">Tahrirlash</button>
        <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="deleteFaculty(${f.id})">O'chirish</button>
      </td>
    </tr>
  `).join('');

  // Directions Table
  const dirBody = document.getElementById('directionsTableBody');
  dirBody.innerHTML = allDirections.map(d => `
    <tr>
      <td><b>${d.name}</b> <span style="font-size: 11px; color: var(--text-muted);">${d.code || ''}</span></td>
      <td><span style="font-size: 12px; color: var(--text-secondary);">${d.faculty_name}</span></td>
      <td><span class="badge badge-emerald">${d.clubs_count || 0} ta to'garak</span></td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="editDirection(${d.id})">Tahrirlash</button>
        <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="deleteDirection(${d.id})">O'chirish</button>
      </td>
    </tr>
  `).join('');
}

// Modals: Faculty
function openFacultyModal(fac = null) {
  const modal = document.getElementById('facultyModal');
  const form = document.getElementById('facultyForm');
  form.reset();
  if (fac) {
    document.getElementById('facultyModalTitle').innerText = 'Fakultetni tahrirlash';
    document.getElementById('facultyFormId').value = fac.id;
    document.getElementById('facultyFormName').value = fac.name;
    document.getElementById('facultyFormCode').value = fac.code || '';
  } else {
    document.getElementById('facultyModalTitle').innerText = 'Fakultet qo\'shish';
    document.getElementById('facultyFormId').value = '';
  }
  modal.classList.add('show');
}

function closeFacultyModal() {
  document.getElementById('facultyModal').classList.remove('show');
}

function editFaculty(id) {
  const fac = allFaculties.find(f => f.id === id);
  if (fac) openFacultyModal(fac);
}

async function deleteFaculty(id) {
  if (!confirm('Fakultetni o\'chirmoqchimisiz? Unga tegishli yo\'nalishlar va to\'garaklar ham o\'chiriladi.')) return;
  try {
    const res = await fetch(`/api/v1/faculties/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast('Fakultet o\'chirildi');
    await loadAcademicTables();
  } catch (err) {
    showToast('Fakultetni o\'chirishda xatolik yuz berdi', 'error');
  }
}

// Modals: Direction
function openDirectionModal(dir = null) {
  const modal = document.getElementById('directionModal');
  const form = document.getElementById('directionForm');
  form.reset();
  if (dir) {
    document.getElementById('directionModalTitle').innerText = 'Yo\'nalishni tahrirlash';
    document.getElementById('directionFormId').value = dir.id;
    document.getElementById('directionFormFacultyId').value = dir.faculty_id;
    document.getElementById('directionFormName').value = dir.name;
    document.getElementById('directionFormCode').value = dir.code || '';
  } else {
    document.getElementById('directionModalTitle').innerText = 'Yo\'nalish qo\'shish';
    document.getElementById('directionFormId').value = '';
  }
  modal.classList.add('show');
}

function closeDirectionModal() {
  document.getElementById('directionModal').classList.remove('show');
}

function editDirection(id) {
  const dir = allDirections.find(d => d.id === id);
  if (dir) openDirectionModal(dir);
}

async function deleteDirection(id) {
  if (!confirm('Yo\'nalishni o\'chirmoqchimisiz?')) return;
  try {
    const res = await fetch(`/api/v1/directions/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast('Yo\'nalish o\'chirildi');
    await loadAcademicTables();
  } catch (err) {
    showToast('Yo\'nalishni o\'chirishda xatolik yuz berdi', 'error');
  }
}

// Setup Form Submit Listeners
function setupForms() {
  // Club Submit
  document.getElementById('clubForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('clubFormId').value;
    const payload = {
      direction_id: parseInt(document.getElementById('clubFormDirectionId').value),
      name: document.getElementById('clubFormName').value.trim(),
      description: document.getElementById('clubFormDesc').value.trim(),
      schedule_days: document.getElementById('clubFormDays').value.trim(),
      schedule_time: document.getElementById('clubFormTime').value.trim(),
      room_location: document.getElementById('clubFormRoom').value.trim(),
      leader_name: document.getElementById('clubFormLeaderName').value.trim(),
      leader_contact: document.getElementById('clubFormLeaderContact').value.trim(),
      max_capacity: 0,
      is_active: true
    };

    try {
      const url = id ? `/api/v1/clubs/${id}` : '/api/v1/clubs';
      const method = id ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Saqlashda xatolik');
      }

      showToast(id ? 'To\'garak ma\'lumotlari yangilandi' : 'Yangi to\'garak yaratildi');
      closeClubModal();
      await loadClubs();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Faculty Submit
  document.getElementById('facultyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('facultyFormId').value;
    const payload = {
      name: document.getElementById('facultyFormName').value.trim(),
      code: document.getElementById('facultyFormCode').value.trim() || null,
      is_active: true
    };

    try {
      const url = id ? `/api/v1/faculties/${id}` : '/api/v1/faculties';
      const method = id ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Saqlashda xatolik');
      showToast('Fakultet saqlandi');
      closeFacultyModal();
      await loadAcademicTables();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Direction Submit
  document.getElementById('directionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('directionFormId').value;
    const payload = {
      faculty_id: parseInt(document.getElementById('directionFormFacultyId').value),
      name: document.getElementById('directionFormName').value.trim(),
      code: document.getElementById('directionFormCode').value.trim() || null,
      is_active: true
    };

    try {
      const url = id ? `/api/v1/directions/${id}` : '/api/v1/directions';
      const method = id ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Saqlashda xatolik');
      showToast('Yo\'nalish saqlandi');
      closeDirectionModal();
      await loadAcademicTables();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

// Load Channel Setting
async function loadChannelSettings() {
  try {
    const res = await fetch('/api/v1/settings/channel');
    if (res.ok) {
      const data = await res.json();
      if (data.channel_id) {
        document.getElementById('telegramChannelInput').value = data.channel_id;
      }
    }
  } catch (err) {
    console.error('Failed to load channel setting:', err);
  }
}

async function sendTestChannelPing() {
  const channelInput = document.getElementById('telegramChannelInput');
  const channelId = channelInput.value.trim();
  if (!channelId) {
    showToast('Iltimos avval kanal username yoki ID sini kiriting', 'error');
    return;
  }

  const btn = document.getElementById('btnTestChannel');
  btn.disabled = true;
  btn.innerText = 'Yuborilmoqda...';

  try {
    const res = await fetch('/api/v1/settings/test-channel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel_id: channelId })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Xabar yuborishda xatolik');
    showToast(data.message, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerText = '🔔 Sinov xabari yuborish';
  }
}

// Setup Form Submit Listeners
function setupForms() {
  // Telegram Channel Save Submit
  document.getElementById('telegramChannelForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const channelId = document.getElementById('telegramChannelInput').value.trim();
    if (!channelId) return;

    try {
      const res = await fetch('/api/v1/settings/channel', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel_id: channelId })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Saqlashda xatolik');
      showToast('Boshqaruv kanali muvaffaqiyatli saqlandi!');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Telegram Personal Chat ID Settings Submit
  document.getElementById('telegramChatIdForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const chatId = parseInt(document.getElementById('telegramChatIdInput').value);
    if (!chatId) {
      showToast('Iltimos to\'g\'ri Telegram ID kiriting', 'error');
      return;
    }

    try {
      const res = await fetch('/api/v1/auth/telegram-chat-id', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_chat_id: chatId })
      });

      if (!res.ok) throw new Error('Saqlashda xatolik');
      showToast('Telegram Chat ID muvaffaqiyatli saqlandi!');
    } catch (err) {
      showToast('Saqlashda xatolik yuz berdi', 'error');
    }
  });

  // Change Password Submit
  document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const currentPassword = document.getElementById('currentPasswordInput').value;
    const newPassword = document.getElementById('newPasswordInput').value;
    const confirmPassword = document.getElementById('confirmPasswordInput').value;

    if (newPassword !== confirmPassword) {
      showToast('Yangi parollar bir-biriga mos kelmadi!', 'error');
      return;
    }

    if (newPassword.length < 8) {
      showToast('Yangi parol kamida 8 ta belgidan iborat bo\'lishi kerak!', 'error');
      return;
    }

    try {
      const res = await fetch('/api/v1/auth/change-password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Parolni o\'zgartirishda xatolik');

      showToast(data.message || 'Parol muvaffaqiyatli o\'zgartirildi!', 'success');
      document.getElementById('changePasswordForm').reset();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}
