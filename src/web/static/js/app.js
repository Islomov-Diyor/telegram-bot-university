// State
let allFaculties = [];
let allDirections = [];
let currentClubs = [];
let searchDebounceTimer = null;
let currentActiveTab = 'dashboard';
let autoRefreshTimer = null;

// Authenticated API Fetch Helper
async function apiFetch(url, options = {}) {
  options.headers = options.headers || {};
  const token = localStorage.getItem('access_token');
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }
  options.credentials = 'include';

  try {
    const response = await fetch(url, options);
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('admin_user');
      window.location.href = '/login';
      throw new Error('Not authenticated.');
    }
    return response;
  } catch (err) {
    if (err.message === 'Not authenticated.') {
      window.location.href = '/login';
    }
    throw err;
  }
}

// Toast notification
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
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

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuth();
  setupNavigation();
  await loadInitialData();

  // Restore active tab from URL hash or localStorage
  const hashTab = window.location.hash.replace('#', '');
  const savedTab = hashTab || localStorage.getItem('admin_active_tab') || 'dashboard';
  await switchTab(savedTab);

  setupForms();

  // Background auto-refresh polling every 12 seconds so bot registrations update live
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  autoRefreshTimer = setInterval(refreshCurrentTabSilent, 12000);
});

// React to language switch
window.onLanguageChanged = async (lang) => {
  populateFacultyDropdowns();
  populateStudentClubDropdown();
  if (currentActiveTab === 'dashboard') {
    await loadDashboardStats();
  } else if (currentActiveTab === 'clubs') {
    await loadClubs();
  } else if (currentActiveTab === 'students') {
    await fetchStudents();
  } else if (currentActiveTab === 'academic') {
    await loadAcademicTables();
  }
};

// Auth Verification
async function checkAuth() {
  try {
    const res = await apiFetch('/api/v1/auth/me');
    if (!res.ok) throw new Error('Not authenticated');
    const admin = await res.json();
    window.currentUser = admin;

    document.getElementById('adminFullName').innerText = admin.full_name;
    document.getElementById('avatarLetter').innerText = admin.full_name.charAt(0).toUpperCase();

    if (admin.role === 'teacher') {
      const clubDesc = admin.club_name ? ` (${admin.club_name})` : '';
      document.getElementById('adminRole').innerText = `O'qituvchi${clubDesc}`;

      // 1. Hide superadmin-only tabs
      const navDashboard = document.getElementById('navDashboard');
      if (navDashboard) navDashboard.style.display = 'none';
      const tabDashboard = document.getElementById('tab-dashboard');
      if (tabDashboard) tabDashboard.style.display = 'none';

      const navTeachers = document.getElementById('navTeachers');
      if (navTeachers) navTeachers.style.display = 'none';
      const navAcademic = document.getElementById('navAcademic');
      if (navAcademic) navAcademic.style.display = 'none';
      const navSettings = document.getElementById('navSettings');
      if (navSettings) navSettings.style.display = 'none';

      // 2. Rename navigation menu for Teacher
      const navClubsText = document.getElementById('navClubsText');
      if (navClubsText) navClubsText.innerText = "Mening To'garagim";
      const navStudentsText = document.getElementById('navStudentsText');
      if (navStudentsText) navStudentsText.innerText = "Talabalarim";
      const navBroadcastText = document.getElementById('navBroadcastText');
      if (navBroadcastText) navBroadcastText.innerText = "O'z To'garagimga Xabar";

      // 3. Customize pages for Teacher
      const btnAddClubHeader = document.getElementById('btnAddClubHeader');
      if (btnAddClubHeader) btnAddClubHeader.style.display = 'none';
      const clubFilterToolbar = document.getElementById('clubFilterToolbar');
      if (clubFilterToolbar) clubFilterToolbar.style.display = 'none';

      const clubsPageTitle = document.getElementById('clubsPageTitle');
      if (clubsPageTitle) clubsPageTitle.innerText = "Mening To'garagim";
      const clubsPageDesc = document.getElementById('clubsPageDesc');
      if (clubsPageDesc) clubsPageDesc.innerText = "O'zingizga biriktirilgan to'garak va mashg'ulotlar faoliyati";

      const studentsPageTitle = document.getElementById('studentsPageTitle');
      if (studentsPageTitle) studentsPageTitle.innerText = "Talabalarim Ro'yxati";
      const studentsPageDesc = document.getElementById('studentsPageDesc');
      if (studentsPageDesc) studentsPageDesc.innerText = "To'garagingizga a'zo bo'lgan talabalar va ularning aloqa ma'lumotlari";

      const studentFilterFaculty = document.getElementById('studentFilterFaculty');
      if (studentFilterFaculty) studentFilterFaculty.style.display = 'none';
      const studentFilterClub = document.getElementById('studentFilterClub');
      if (studentFilterClub) studentFilterClub.style.display = 'none';

      // 4. Set teacher default active tab to 'clubs'
      if (!currentActiveTab || currentActiveTab === 'dashboard' || ['academic', 'settings', 'teachers'].includes(currentActiveTab)) {
        currentActiveTab = 'clubs';
      }
    } else {
      document.getElementById('adminRole').innerText = 'Super Admin';
    }

    if (admin.telegram_chat_id) {
      const chatInput = document.getElementById('telegramChatIdInput');
      if (chatInput) chatInput.value = admin.telegram_chat_id;
    }
  } catch (err) {
    window.location.href = '/login';
  }
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', async () => {
  try {
    await apiFetch('/api/v1/auth/logout', { method: 'POST' });
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('admin_user');
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

  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash && hash !== currentActiveTab) {
      switchTab(hash);
    }
  });
}

async function switchTab(tabName) {
  currentActiveTab = tabName;
  localStorage.setItem('admin_active_tab', tabName);
  if (window.location.hash !== '#' + tabName) {
    history.replaceState(null, '', '#' + tabName);
  }

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
  } else if (tabName === 'attendance') {
    await loadAttendanceTab();
  } else if (tabName === 'broadcast') {
    await loadBroadcastTab();
  } else if (tabName === 'teachers') {
    await loadTeachersTab();
  } else if (tabName === 'academic') {
    await loadAcademicTables();
  } else if (tabName === 'settings') {
    await loadChannelSettings();
  }
}


// Manual Refresh Button Action
async function manualRefresh() {
  const icon = document.getElementById('refreshIcon');
  if (icon) icon.style.animation = 'spin 1s linear infinite';

  try {
    await switchTab(currentActiveTab);
    showToast(t('toast_data_refreshed'), 'success');
  } catch (err) {
    showToast(t('toast_refresh_error'), 'error');
  } finally {
    if (icon) {
      setTimeout(() => { icon.style.animation = 'none'; }, 600);
    }
  }
}

// Silent background refresh
async function refreshCurrentTabSilent() {
  try {
    if (currentActiveTab === 'dashboard') {
      await loadDashboardStats();
    } else if (currentActiveTab === 'students') {
      const searchInput = document.getElementById('studentSearchInput');
      if (document.activeElement !== searchInput) {
        await fetchStudents();
      }
    }
  } catch (err) {
    // Ignore silent background refresh errors
  }
}

// Initial Common Data
async function loadInitialData() {
  try {
    if (window.currentUser && window.currentUser.role === 'teacher') {
      const clubsRes = await apiFetch('/api/v1/clubs');
      if (clubsRes.ok) {
        currentClubs = await clubsRes.json();
      }
      populateStudentClubDropdown();
      return;
    }

    const [facRes, dirRes, clubsRes] = await Promise.all([
      apiFetch('/api/v1/faculties'),
      apiFetch('/api/v1/directions'),
      apiFetch('/api/v1/clubs')
    ]);

    const facData = await facRes.json();
    const dirData = await dirRes.json();
    const clubsData = await clubsRes.json();

    allFaculties = Array.isArray(facData) ? facData : [];
    allDirections = Array.isArray(dirData) ? dirData : [];
    currentClubs = Array.isArray(clubsData) ? clubsData : [];

    populateFacultyDropdowns();
    populateStudentClubDropdown();
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
    const defaultText = isFilter ? t('filter_all_faculties') : t('filter_select_faculty');
    el.innerHTML = `<option value="">${defaultText}</option>`;
    if (Array.isArray(allFaculties)) {
      allFaculties.forEach(fac => {
        el.innerHTML += `<option value="${fac.id}">${fac.name}</option>`;
      });
    }
  });

  // Populate direction dropdown in Club modal
  const clubDirSelect = document.getElementById('clubFormDirectionId');
  if (clubDirSelect) {
    clubDirSelect.innerHTML = `<option value="">${t('filter_select_direction')}</option>`;
    if (Array.isArray(allDirections)) {
      allDirections.forEach(dir => {
        clubDirSelect.innerHTML += `<option value="${dir.id}">${dir.faculty_name ? dir.faculty_name + ' -> ' : ''}${dir.name}</option>`;
      });
    }
  }
}

function populateStudentClubDropdown() {
  const clubSelect = document.getElementById('studentFilterClub');
  if (!clubSelect) return;
  const currentVal = clubSelect.value;
  clubSelect.innerHTML = `<option value="">${t('filter_all_clubs')}</option>`;
  if (Array.isArray(currentClubs)) {
    currentClubs.forEach(c => {
      clubSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
  }
  if (currentVal) clubSelect.value = currentVal;
}

// 1. DASHBOARD
async function loadDashboardStats() {
  try {
    const res = await apiFetch('/api/v1/stats/overview');
    const data = await res.json();

    document.getElementById('kpiStudents').innerText = data.students_count || 0;
    if (document.getElementById('kpiWaiting')) {
      document.getElementById('kpiWaiting').innerText = data.waiting_count || 0;
    }
    document.getElementById('kpiClubs').innerText = data.clubs_count || 0;
    document.getElementById('kpiFaculties').innerText = data.faculties_count || 0;
    document.getElementById('kpiDirections').innerText = data.directions_count || 0;

    // Top clubs
    const topClubsList = document.getElementById('topClubsList');
    if (!data.top_clubs || data.top_clubs.length === 0) {
      topClubsList.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">${t('no_members_yet')}</p>`;
    } else {
      topClubsList.innerHTML = data.top_clubs.map(c => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(11, 15, 25, 0.4); border-radius: var(--radius-md);">
          <span style="font-size: 13px; font-weight: 500;">🎯 ${c.name}</span>
          <span class="badge badge-indigo">${c.count} ${t('students_count_suffix')}</span>
        </div>
      `).join('');
    }

    // Faculty breakdown
    const facList = document.getElementById('facultyBreakdownList');
    if (!data.faculty_breakdown || data.faculty_breakdown.length === 0) {
      facList.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">${t('no_data')}</p>`;
    } else {
      facList.innerHTML = data.faculty_breakdown.map(f => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(11, 15, 25, 0.4); border-radius: var(--radius-md);">
          <span style="font-size: 13px; font-weight: 500;">🏛 ${f.name}</span>
          <span class="badge badge-emerald">${f.count} ${t('people_suffix')}</span>
        </div>
      `).join('');
    }

    await loadRecentRegistrations();
  } catch (err) {
    console.error('Error loading dashboard stats:', err);
  }
}

async function loadRecentRegistrations() {
  const tbody = document.getElementById('recentStudentsTableBody');
  if (!tbody) return;

  try {
    const res = await apiFetch('/api/v1/registrations/recent?limit=8');
    const items = await res.json();

    if (!Array.isArray(items) || items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 24px;">${t('no_recent_students')}</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map((item, idx) => {
      const regDate = item.registered_at ? new Date(item.registered_at).toLocaleDateString(getCurrentLanguage() === 'en' ? 'en-US' : 'uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '-';
      const statusBadge = item.status === 'active'
        ? `<span class="badge badge-emerald">${t('status_active')}</span>`
        : `<span class="badge badge-amber">${t('status_waiting', { pos: item.queue_position || 1 })}</span>`;

      return `
        <tr>
          <td><b>${idx + 1}</b></td>
          <td><b>${item.full_name}</b></td>
          <td><span class="badge badge-indigo">${item.club_name}</span></td>
          <td style="font-size: 12px;">${item.faculty_name}</td>
          <td><span class="badge badge-indigo">${item.course_level}-${t('th_course')}</span></td>
          <td>${statusBadge}</td>
          <td><a href="tel:${item.phone_number}" style="color: var(--text-primary); text-decoration: none;">${item.phone_number}</a></td>
          <td style="font-size: 11px; color: var(--text-secondary);">${regDate}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading recent registrations:', err);
  }
}

// 2. CLUBS MANAGEMENT
async function loadClubs() {
  const facId = document.getElementById('clubFilterFaculty').value;
  let url = '/api/v1/clubs';
  if (facId) url += `?faculty_id=${facId}`;

  try {
    const res = await apiFetch(url);
    const data = await res.json();
    currentClubs = Array.isArray(data) ? data : [];
    document.getElementById('clubsCountBadge').innerText = t('clubs_count_suffix', { count: currentClubs.length });

    populateStudentClubDropdown();

    const grid = document.getElementById('clubsGrid');
    if (currentClubs.length === 0) {
      grid.innerHTML = `<p style="color: var(--text-muted); font-size: 13px; grid-column: 1/-1;">${t('no_clubs_found')}</p>`;
      return;
    }

    grid.innerHTML = currentClubs.map(c => {
      // Capacity badge
      let capacityBadge = '';
      if (c.max_capacity > 0) {
        if (c.is_full) {
          capacityBadge = `<span class="badge badge-amber">${t('status_full', { cur: c.students_count, max: c.max_capacity, wait: c.waiting_students_count || 0 })}</span>`;
        } else {
          capacityBadge = `<span class="badge badge-emerald">${t('status_spots', { cur: c.students_count, max: c.max_capacity })}</span>`;
        }
      } else {
        capacityBadge = `<span class="badge badge-emerald">${t('status_unlimited', { cur: c.students_count })}</span>`;
      }

      // Deadline badge
      let deadlineBadge = '';
      if (c.registration_deadline) {
        const dl = new Date(c.registration_deadline);
        const dlFormatted = dl.toLocaleDateString(getCurrentLanguage() === 'en' ? 'en-US' : 'uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
        if (c.is_deadline_passed) {
          deadlineBadge = `<span class="badge badge-rose">${t('status_deadline_passed', { date: dlFormatted })}</span>`;
        } else {
          deadlineBadge = `<span class="badge badge-indigo">${t('status_deadline_open', { date: dlFormatted })}</span>`;
        }
      }

      return `
        <div class="glass-panel club-card">
          <div>
            <div class="club-header" style="flex-wrap: wrap; gap: 6px;">
              <div class="badge badge-indigo">${c.faculty_name || 'Fakultet'}</div>
              ${capacityBadge}
              ${deadlineBadge}
            </div>
            <h3 class="club-title">${c.name}</h3>
            <p class="club-desc">${c.description}</p>
            <div class="club-meta-list">
              <div class="club-meta-item"><span>📚</span> <span><b>${t('th_direction')}:</b> ${c.direction_name || '-'}</span></div>
              <div class="club-meta-item"><span>🗓</span> <span><b>${t('th_schedule')}:</b> ${c.schedule_days} (${c.schedule_time})</span></div>
              <div class="club-meta-item"><span>📍</span> <span><b>${t('form_club_room')}:</b> ${c.room_location}</span></div>
              <div class="club-meta-item"><span>👨‍🏫</span> <span><b>${t('form_club_leader')}:</b> ${c.leader_name}</span></div>
              <div class="club-meta-item"><span>📞</span> <span><b>${t('form_club_contact')}:</b> ${c.leader_contact}</span></div>
            </div>
          </div>
          <div class="club-footer" style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="editClub(${c.id})">
              ✏️ ${t('edit')}
            </button>
            <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px; border-color: rgba(245, 158, 11, 0.4); color: #FBBF24;" onclick="triggerClubReminderDirect(${c.id}, '${(c.name || '').replace(/'/g, "\\'")}')">
              🔔 ${t('btn_send_reminder') || 'Dars eslatmasi'}
            </button>
            ${window.currentUser && window.currentUser.role === 'teacher' ? '' : `
              <button class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="deleteClub(${c.id})">
                🗑 ${t('delete')}
              </button>
            `}
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    showToast(t('toast_refresh_error'), 'error');
  }
}

async function triggerClubReminderDirect(clubId, clubName) {
  if (!confirm(`“${clubName}” a'zolariga Telegram orqali bugungi mashg‘ulot eslatmasini yuborishni tasdiqlaysizmi?`)) {
    return;
  }
  try {
    const res = await apiFetch(`/api/v1/clubs/${clubId}/remind`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Eslatma yuborishda xatolik');
    showToast(data.message, 'success');
  } catch (err) {
    showToast(err.message, 'error');
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
    document.getElementById('clubModalTitle').innerText = t('modal_edit_club');
    document.getElementById('clubFormId').value = clubData.id;
    document.getElementById('clubFormDirectionId').value = clubData.direction_id;
    document.getElementById('clubFormName').value = clubData.name;
    document.getElementById('clubFormDesc').value = clubData.description;
    document.getElementById('clubFormDays').value = clubData.schedule_days;
    document.getElementById('clubFormTime').value = clubData.schedule_time;
    document.getElementById('clubFormRoom').value = clubData.room_location;
    document.getElementById('clubFormLeaderName').value = clubData.leader_name;
    document.getElementById('clubFormLeaderContact').value = clubData.leader_contact;
    document.getElementById('clubFormMaxCapacity').value = clubData.max_capacity || 0;

    if (clubData.registration_deadline) {
      const dt = new Date(clubData.registration_deadline);
      const year = dt.getFullYear();
      const month = String(dt.getMonth() + 1).padStart(2, '0');
      const day = String(dt.getDate()).padStart(2, '0');
      const hours = String(dt.getHours()).padStart(2, '0');
      const mins = String(dt.getMinutes()).padStart(2, '0');
      document.getElementById('clubFormDeadline').value = `${year}-${month}-${day}T${hours}:${mins}`;
    } else {
      document.getElementById('clubFormDeadline').value = '';
    }
  } else {
    document.getElementById('clubModalTitle').innerText = t('modal_add_club');
    document.getElementById('clubFormId').value = '';
    document.getElementById('clubFormMaxCapacity').value = 20;
    document.getElementById('clubFormDeadline').value = '';
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
  if (!confirm(t('confirm_delete_club'))) return;
  try {
    const res = await apiFetch(`/api/v1/clubs/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast(t('toast_club_deleted'), 'success');
    await loadClubs();
    await loadInitialData();
  } catch (err) {
    showToast(t('toast_refresh_error'), 'error');
  }
}

// 3. STUDENTS REGISTRATIONS
async function fetchStudents() {
  const isTeacher = window.currentUser && window.currentUser.role === 'teacher';
  const facultyId = isTeacher ? '' : document.getElementById('studentFilterFaculty').value;
  const clubId = isTeacher && window.currentUser.club_id ? window.currentUser.club_id : document.getElementById('studentFilterClub').value;
  const courseLevel = document.getElementById('studentFilterCourse').value;
  const statusEl = document.getElementById('studentFilterStatus');
  const statusVal = statusEl ? statusEl.value : '';
  const search = document.getElementById('studentSearchInput').value.trim();

  let params = new URLSearchParams();
  if (facultyId) params.append('faculty_id', facultyId);
  if (clubId) params.append('club_id', clubId);
  if (courseLevel) params.append('course_level', courseLevel);
  if (statusVal) params.append('status', statusVal);
  if (search) params.append('search', search);

  document.getElementById('btnExportExcel').href = `/api/v1/export/excel?${params.toString()}`;
  document.getElementById('btnExportCsv').href = `/api/v1/export/csv?${params.toString()}`;

  try {
    const res = await apiFetch(`/api/v1/registrations?${params.toString()}`);
    const data = await res.json();

    const tbody = document.getElementById('studentsTableBody');
    if (!data.items || data.items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--text-muted); padding: 32px;">${t('no_students_found')}</td></tr>`;
      return;
    }

    tbody.innerHTML = data.items.map((item, idx) => {
      const regDate = item.registered_at ? new Date(item.registered_at).toLocaleDateString(getCurrentLanguage() === 'en' ? 'en-US' : 'uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '-';
      const tgText = item.telegram_username ? `<a href="https://t.me/${item.telegram_username}" target="_blank" style="color: #818CF8; text-decoration: none;">@${item.telegram_username}</a>` : '<span style="color: var(--text-muted);">-</span>';

      const statusBadge = item.status === 'active'
        ? `<span class="badge badge-emerald">${t('status_active')}</span>`
        : `<span class="badge badge-amber">${t('status_waiting', { pos: item.queue_position || 1 })}</span>`;

      return `
        <tr>
          <td><b>${idx + 1}</b></td>
          <td><b>${item.full_name}</b></td>
          <td>${item.faculty_name}</td>
          <td>${item.direction_name}</td>
          <td><span class="badge badge-indigo">${item.club_name}</span></td>
          <td><span class="badge badge-emerald">${item.course_level}-${t('th_course')}</span></td>
          <td>${statusBadge}</td>
          <td><a href="tel:${item.phone_number}" style="color: var(--text-primary); text-decoration: none;">${item.phone_number}</a></td>
          <td>${tgText}</td>
          <td style="font-size: 11px; color: var(--text-secondary);">${regDate}</td>
          <td>
            <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="deleteRegistration(${item.id})">
              ${t('cancel_reg')}
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    showToast(t('toast_refresh_error'), 'error');
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
  clubSelect.innerHTML = `<option value="">${t('filter_all_clubs')}</option>`;

  const filtered = facId ? currentClubs.filter(c => c.faculty_id == facId) : currentClubs;
  filtered.forEach(c => {
    clubSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
  });

  fetchStudents();
}

async function deleteRegistration(id) {
  if (!confirm(t('confirm_cancel_reg'))) return;
  try {
    const res = await apiFetch(`/api/v1/registrations/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Xatolik yuz berdi');

    showToast(data.message || 'Muvaffaqiyatli bekor qilindi', 'success');
    await fetchStudents();
    await loadDashboardStats();
  } catch (err) {
    showToast(err.message || 'Xatolik yuz berdi', 'error');
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
      <td><span class="badge badge-indigo">${t('directions_count_badge', { count: f.directions_count || 0 })}</span></td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="editFaculty(${f.id})">${t('edit')}</button>
        <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="deleteFaculty(${f.id})">${t('delete')}</button>
      </td>
    </tr>
  `).join('');

  // Directions Table
  const dirBody = document.getElementById('directionsTableBody');
  dirBody.innerHTML = allDirections.map(d => `
    <tr>
      <td><b>${d.name}</b> <span style="font-size: 11px; color: var(--text-muted);">${d.code || ''}</span></td>
      <td><span style="font-size: 12px; color: var(--text-secondary);">${d.faculty_name}</span></td>
      <td><span class="badge badge-emerald">${t('clubs_count_suffix', { count: d.clubs_count || 0 })}</span></td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="editDirection(${d.id})">${t('edit')}</button>
        <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="deleteDirection(${d.id})">${t('delete')}</button>
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
    document.getElementById('facultyModalTitle').innerText = t('modal_edit_faculty');
    document.getElementById('facultyFormId').value = fac.id;
    document.getElementById('facultyFormName').value = fac.name;
    document.getElementById('facultyFormCode').value = fac.code || '';
  } else {
    document.getElementById('facultyModalTitle').innerText = t('modal_add_faculty');
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
  if (!confirm(t('confirm_delete_faculty'))) return;
  try {
    const res = await apiFetch(`/api/v1/faculties/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast(t('toast_faculty_deleted'), 'success');
    await loadAcademicTables();
  } catch (err) {
    showToast(t('toast_refresh_error'), 'error');
  }
}

// Modals: Direction
function openDirectionModal(dir = null) {
  const modal = document.getElementById('directionModal');
  const form = document.getElementById('directionForm');
  form.reset();
  if (dir) {
    document.getElementById('directionModalTitle').innerText = t('modal_edit_direction');
    document.getElementById('directionFormId').value = dir.id;
    document.getElementById('directionFormFacultyId').value = dir.faculty_id;
    document.getElementById('directionFormName').value = dir.name;
    document.getElementById('directionFormCode').value = dir.code || '';
  } else {
    document.getElementById('directionModalTitle').innerText = t('modal_add_direction');
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
  if (!confirm(t('confirm_delete_direction'))) return;
  try {
    const res = await apiFetch(`/api/v1/directions/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast(t('toast_direction_deleted'), 'success');
    await loadAcademicTables();
  } catch (err) {
    showToast(t('toast_refresh_error'), 'error');
  }
}

// Load Channel Setting
async function loadChannelSettings() {
  try {
    const res = await apiFetch('/api/v1/settings/channel');
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
    showToast('Iltimos kanal username yoki ID sini kiriting', 'error');
    return;
  }

  const btn = document.getElementById('btnTestChannel');
  btn.disabled = true;
  btn.innerText = '...';

  try {
    const res = await apiFetch('/api/v1/settings/test-channel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel_id: channelId })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Xatolik');
    showToast(data.message, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerText = t('btn_test_ping');
  }
}

// Setup Form Submit Listeners
function setupForms() {
  // Club Submit
  document.getElementById('clubForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('clubFormId').value;
    const deadlineVal = document.getElementById('clubFormDeadline').value;
    const maxCapVal = parseInt(document.getElementById('clubFormMaxCapacity').value || '0', 10);

    const payload = {
      direction_id: parseInt(document.getElementById('clubFormDirectionId').value),
      name: document.getElementById('clubFormName').value.trim(),
      description: document.getElementById('clubFormDesc').value.trim(),
      schedule_days: document.getElementById('clubFormDays').value.trim(),
      schedule_time: document.getElementById('clubFormTime').value.trim(),
      room_location: document.getElementById('clubFormRoom').value.trim(),
      leader_name: document.getElementById('clubFormLeaderName').value.trim(),
      leader_contact: document.getElementById('clubFormLeaderContact').value.trim(),
      max_capacity: isNaN(maxCapVal) ? 0 : maxCapVal,
      registration_deadline: deadlineVal ? new Date(deadlineVal).toISOString() : null,
      is_active: true
    };

    try {
      const url = id ? `/api/v1/clubs/${id}` : '/api/v1/clubs';
      const method = id ? 'PUT' : 'POST';
      const res = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Saqlashda xatolik');
      }

      showToast(id ? t('toast_club_saved') : t('toast_club_created'), 'success');
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
      const res = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Saqlashda xatolik');
      showToast(t('toast_faculty_saved'), 'success');
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
      const res = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Saqlashda xatolik');
      showToast(t('toast_direction_saved'), 'success');
      closeDirectionModal();
      await loadAcademicTables();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Telegram Channel Save Submit
  document.getElementById('telegramChannelForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const channelId = document.getElementById('telegramChannelInput').value.trim();
    if (!channelId) return;

    try {
      const res = await apiFetch('/api/v1/settings/channel', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel_id: channelId })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Xatolik');
      showToast(t('toast_channel_saved'), 'success');
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
      const res = await apiFetch('/api/v1/auth/telegram-chat-id', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_chat_id: chatId })
      });

      if (!res.ok) throw new Error('Xatolik');
      showToast(t('toast_chat_id_saved'), 'success');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Change Password Submit
  document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const currentPassword = document.getElementById('currentPasswordInput').value;
    const newPassword = document.getElementById('newPasswordInput').value;
    const confirmPassword = document.getElementById('confirmPasswordInput').value;

    if (newPassword !== confirmPassword) {
      showToast(t('toast_password_mismatch'), 'error');
      return;
    }

    if (newPassword.length < 8) {
      showToast(t('toast_password_min_len'), 'error');
      return;
    }

    try {
      const res = await apiFetch('/api/v1/auth/change-password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Parolni o\'zgartirishda xatolik');

      showToast(t('toast_password_changed'), 'success');
      document.getElementById('changePasswordForm').reset();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Broadcast Form Submit
  const broadcastForm = document.getElementById('broadcastForm');
  if (broadcastForm) {
    broadcastForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const message = document.getElementById('broadcastMessageInput').value.trim();
      if (!message) {
        showToast('Iltimos xabar matnini kiriting', 'error');
        return;
      }

      const isTeacher = window.currentUser && window.currentUser.role === 'teacher';
      const target = isTeacher ? 'club' : (document.querySelector('input[name="broadcastTarget"]:checked')?.value || 'all');
      let clubId = null;
      if (target === 'club') {
        clubId = isTeacher && window.currentUser.club_id 
          ? window.currentUser.club_id 
          : parseInt(document.getElementById('broadcastClubSelect').value);
        if (!clubId) {
          showToast('Iltimos to\'garakni tanlang', 'error');
          return;
        }
      }

      const targetDesc = target === 'all' 
        ? "barcha ro'yxatdan o'tgan foydalanuvchilarga" 
        : "tanlangan to'garak a'zolariga";
      if (!confirm(`Xabarni ${targetDesc} Telegram bot orqali yuborishni tasdiqlaysizmi?`)) {
        return;
      }

      const btn = document.getElementById('btnSubmitBroadcast');
      const banner = document.getElementById('broadcastStatusBanner');
      btn.disabled = true;
      btn.innerText = 'Yuborilmoqda... ⏳';

      try {
        const res = await apiFetch('/api/v1/broadcast', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, target, club_id: clubId })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Xatolik');

        showToast(data.message, 'success');
        banner.style.display = 'block';
        banner.innerHTML = `
          <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); padding: 14px; border-radius: var(--radius-md); color: #34D399; font-size: 13.5px;">
            ✅ <b>Xabar muvaffaqiyatli yetkazildi!</b><br>
            Jami: ${data.total} ta | Yetkazildi: ${data.sent} ta ${data.failed > 0 ? `| Xatolik: ${data.failed} ta` : ''}
          </div>
        `;
        document.getElementById('broadcastMessageInput').value = '';
        updateBroadcastPreview();
      } catch (err) {
        showToast(err.message, 'error');
        banner.style.display = 'block';
        banner.innerHTML = `
          <div style="background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); padding: 14px; border-radius: var(--radius-md); color: #FB7185; font-size: 13.5px;">
            ⚠️ ${err.message}
          </div>
        `;
      } finally {
        btn.disabled = false;
        btn.innerText = '🚀 Yuborish';
      }
    });
  }

  // Teacher Form Submit
  const teacherForm = document.getElementById('teacherForm');
  if (teacherForm) {
    teacherForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('teacherFormId').value;
      const fullName = document.getElementById('teacherFormFullName').value.trim();
      const username = document.getElementById('teacherFormUsername').value.trim();
      const password = document.getElementById('teacherFormPassword').value;
      const clubIdVal = document.getElementById('teacherFormClubId').value;
      const clubId = clubIdVal ? parseInt(clubIdVal) : null;
      const isActive = document.getElementById('teacherFormIsActive').checked;

      if (!fullName) {
        showToast('Iltimos, o‘qituvchi F.I.Sh kiriting', 'error');
        return;
      }
      if (!username) {
        showToast('Iltimos, o‘qituvchi loginini kiriting', 'error');
        return;
      }

      try {
        let res;
        if (id) {
          const payload = { full_name: fullName, club_id: clubId, is_active: isActive };
          if (password) {
            if (password.length < 6) {
              showToast('Yangi parol kamida 6 ta belgidan iborat bo‘lishi kerak', 'error');
              return;
            }
            payload.new_password = password;
          }
          res = await apiFetch(`/api/v1/teachers/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
        } else {
          if (!password) {
            showToast('Iltimos, yangi o‘qituvchi uchun parol kiriting', 'error');
            return;
          }
          if (password.length < 6) {
            showToast('Parol kamida 6 ta belgidan iborat bo‘lishi kerak', 'error');
            return;
          }
          res = await apiFetch('/api/v1/teachers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, full_name: fullName, club_id: clubId })
          });
        }

        const data = await res.json();
        if (!res.ok) {
          let errorMsg = 'Xatolik yuz berdi';
          if (typeof data.detail === 'string') {
            errorMsg = data.detail;
          } else if (Array.isArray(data.detail) && data.detail.length > 0) {
            errorMsg = data.detail[0].msg || JSON.stringify(data.detail);
          }
          throw new Error(errorMsg);
        }

        showToast(id ? 'O‘qituvchi yangilandi' : 'Yangi o‘qituvchi muvaffaqiyatli yaratildi!', 'success');
        closeTeacherModal();
        await loadTeachersTab();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Attendance Lesson Form Submit
  const attendanceLessonForm = document.getElementById('attendanceLessonForm');
  if (attendanceLessonForm) {
    attendanceLessonForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const isTeacher = window.currentUser && window.currentUser.role === 'teacher';
      const clubId = isTeacher && window.currentUser.club_id 
        ? window.currentUser.club_id 
        : parseInt(document.getElementById('lessonModalClubId').value);
      const lessonDate = document.getElementById('lessonModalDate').value;
      const topic = document.getElementById('lessonModalTopic').value.trim();

      try {
        const res = await apiFetch('/api/v1/attendance/lessons', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            club_id: clubId,
            lesson_date: lessonDate,
            topic: topic || null
          })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Darsni ochib bo\'lmadi');

        showToast('Yangi dars davomati ochildi!', 'success');
        closeAttendanceLessonModal();
        currentAttendanceClubId = clubId;
        const select = document.getElementById('attendanceClubSelect');
        if (select) select.value = clubId;

        await loadLessonsList();
        if (data.id) {
          await selectAttendanceLesson(data.id);
        }
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Backdrop click dismiss for all modals
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('show');
        modal.classList.remove('active');
      }
    });
  });
}

// ==========================================
// 8. ATTENDANCE & RESULTS LOGIC
// ==========================================
let currentAttendanceClubId = null;
let currentAttendanceLessonId = null;
let currentLessonRoster = [];

async function loadAttendanceTab() {
  const select = document.getElementById('attendanceClubSelect');
  if (!select) return;

  if (!currentClubs || currentClubs.length === 0) {
    const res = await apiFetch('/api/v1/clubs');
    if (res.ok) currentClubs = await res.json();
  }

  select.innerHTML = '';
  currentClubs.forEach(club => {
    const opt = document.createElement('option');
    opt.value = club.id;
    opt.textContent = `${club.name} (${club.leader_name})`;
    select.appendChild(opt);
  });

  if (window.currentUser && window.currentUser.role === 'teacher' && window.currentUser.club_id) {
    select.value = window.currentUser.club_id;
    select.disabled = true;
  }

  if (select.value) {
    currentAttendanceClubId = parseInt(select.value);
    await loadLessonsList();
    await loadAttendanceResults();
  }
}

async function onAttendanceClubChange() {
  const select = document.getElementById('attendanceClubSelect');
  if (!select) return;
  currentAttendanceClubId = parseInt(select.value);
  currentAttendanceLessonId = null;
  await loadLessonsList();
  await loadAttendanceResults();
}

function switchAttendanceSubView(view) {
  const rosterView = document.getElementById('attendanceRosterView');
  const resultsView = document.getElementById('attendanceResultsView');
  const btnRoster = document.getElementById('btnSubnavRoster');
  const btnResults = document.getElementById('btnSubnavResults');

  if (view === 'roster') {
    rosterView.style.display = 'grid';
    resultsView.style.display = 'none';
    btnRoster.classList.add('active');
    btnResults.classList.remove('active');
  } else {
    rosterView.style.display = 'none';
    resultsView.style.display = 'block';
    btnRoster.classList.remove('active');
    btnResults.classList.add('active');
    loadAttendanceResults();
  }
}

async function loadLessonsList() {
  if (!currentAttendanceClubId) return;
  const container = document.getElementById('lessonsListContainer');
  const badge = document.getElementById('lessonsCountBadge');
  if (!container) return;

  try {
    const res = await apiFetch(`/api/v1/attendance/lessons?club_id=${currentAttendanceClubId}`);
    if (!res.ok) throw new Error('Darslarni yuklab bo\'lmadi');
    const lessons = await res.json();

    if (badge) badge.innerText = `${lessons.length} ta dars`;

    if (lessons.length === 0) {
      container.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">Hozircha darslar mavjud emas. Yuqoridagi "+ Yangi Dars Davomati" tugmasi orqali dars oching.</p>`;
      document.getElementById('lessonRosterTableBody').innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">Darslar mavjud emas. Yangi dars qo'shing.</td></tr>`;
      currentAttendanceLessonId = null;
      return;
    }

    container.innerHTML = '';
    lessons.forEach((lesson, index) => {
      const card = document.createElement('div');
      card.className = `lesson-list-item ${lesson.id === currentAttendanceLessonId || (!currentAttendanceLessonId && index === 0) ? 'active' : ''}`;
      card.onclick = () => selectAttendanceLesson(lesson.id);

      card.innerHTML = `
        <div>
          <div style="font-weight: 700; font-size: 13px; color: var(--text-primary);">
            📅 ${lesson.lesson_date}
          </div>
          <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">
            ${lesson.topic || 'Mavzusiz dars'}
          </div>
        </div>
        <div style="display: flex; gap: 4px;">
          <span class="badge badge-emerald" style="font-size: 10px;">${lesson.present_count} bor</span>
          ${lesson.absent_count > 0 ? `<span class="badge badge-rose" style="font-size: 10px;">${lesson.absent_count} yo'q</span>` : ''}
        </div>
      `;
      container.appendChild(card);
    });

    if (!currentAttendanceLessonId && lessons.length > 0) {
      await selectAttendanceLesson(lessons[0].id);
    }
  } catch (err) {
    container.innerHTML = `<p style="color: var(--accent-rose); font-size: 13px;">${err.message}</p>`;
  }
}

async function selectAttendanceLesson(lessonId) {
  currentAttendanceLessonId = lessonId;

  document.querySelectorAll('.lesson-list-item').forEach(card => card.classList.remove('active'));
  const tableBody = document.getElementById('lessonRosterTableBody');
  tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;">Yuklanmoqda...</td></tr>`;

  try {
    const res = await apiFetch(`/api/v1/attendance/lessons/${lessonId}`);
    if (!res.ok) throw new Error('Dars ro\'yxatini yuklab bo\'lmadi');
    const data = await res.json();

    const lesson = data.lesson;
    document.getElementById('currentLessonTitle').innerText = `📅 Dars: ${lesson.lesson_date} — ${lesson.topic || 'Mavzusiz'}`;
    document.getElementById('currentLessonSubtitle').innerText = `Jami talabalar: ${data.students.length} ta | Hozir: ${lesson.present_count} bor, ${lesson.absent_count} yo'q`;

    currentLessonRoster = data.students;
    renderLessonRosterTable();
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--accent-rose); padding: 20px;">${err.message}</td></tr>`;
  }
}

function renderLessonRosterTable() {
  const tableBody = document.getElementById('lessonRosterTableBody');
  if (!tableBody) return;

  if (currentLessonRoster.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">Ushbu to'garakka a'zo bo'lgan faol talabalar topilmadi.</td></tr>`;
    return;
  }

  tableBody.innerHTML = '';
  currentLessonRoster.forEach((student, idx) => {
    const tr = document.createElement('tr');
    tr.id = `roster-row-${student.student_id}`;

    tr.innerHTML = `
      <td style="color: var(--text-muted);">${idx + 1}</td>
      <td style="font-weight: 600;">${student.full_name}</td>
      <td><span class="badge badge-indigo">${student.course_level}-kurs</span></td>
      <td style="color: var(--text-secondary);">${student.phone_number || '—'}</td>
      <td style="text-align: center;">
        <div class="status-btn-group">
          <button type="button" class="status-btn ${student.status === 'present' ? 'active-present' : ''}" 
                  onclick="setStudentAttendanceStatus(${student.student_id}, 'present')">
            🟢 Bor
          </button>
          <button type="button" class="status-btn ${student.status === 'absent' ? 'active-absent' : ''}" 
                  onclick="setStudentAttendanceStatus(${student.student_id}, 'absent')">
            🔴 Yo'q
          </button>
          <button type="button" class="status-btn ${student.status === 'excused' ? 'active-excused' : ''}" 
                  onclick="setStudentAttendanceStatus(${student.student_id}, 'excused')">
            🟡 Sababli
          </button>
        </div>
      </td>
      <td>
        <input type="text" class="form-input" style="font-size: 12px; padding: 4px 8px; width: 100%;" 
               placeholder="Izoh..." value="${student.notes || ''}" 
               onchange="setStudentAttendanceNotes(${student.student_id}, this.value)">
      </td>
    `;
    tableBody.appendChild(tr);
  });
}

function setStudentAttendanceStatus(studentId, status) {
  const s = currentLessonRoster.find(item => item.student_id === studentId);
  if (s) {
    s.status = status;
    const row = document.getElementById(`roster-row-${studentId}`);
    if (row) {
      const btns = row.querySelectorAll('.status-btn');
      btns[0].className = `status-btn ${status === 'present' ? 'active-present' : ''}`;
      btns[1].className = `status-btn ${status === 'absent' ? 'active-absent' : ''}`;
      btns[2].className = `status-btn ${status === 'excused' ? 'active-excused' : ''}`;
    }
  }
}

function setStudentAttendanceNotes(studentId, notes) {
  const s = currentLessonRoster.find(item => item.student_id === studentId);
  if (s) s.notes = notes.trim();
}

function markAllRosterPresent() {
  currentLessonRoster.forEach(s => s.status = 'present');
  renderLessonRosterTable();
  showToast('Barcha talabalar "Bor" deb belgilandi', 'success');
}

async function saveCurrentLessonAttendance() {
  if (!currentAttendanceLessonId) {
    showToast('Dars tanlanmagan', 'error');
    return;
  }

  const btn = document.getElementById('btnSaveRoster');
  btn.disabled = true;
  btn.innerText = 'Saqlanmoqda...';

  try {
    const payload = {
      records: currentLessonRoster.map(s => ({
        student_id: s.student_id,
        status: s.status,
        notes: s.notes || null
      }))
    };

    const res = await apiFetch(`/api/v1/attendance/lessons/${currentAttendanceLessonId}/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Davomatni saqlab bo\'lmadi');
    showToast('Davomat muvaffaqiyatli saqlandi!', 'success');
    await loadLessonsList();
    await loadAttendanceResults();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerText = '💾 Saqlash';
  }
}

function openAttendanceLessonModal() {
  const modal = document.getElementById('attendanceLessonModal');
  const clubSelect = document.getElementById('lessonModalClubId');
  const dateInput = document.getElementById('lessonModalDate');
  const topicInput = document.getElementById('lessonModalTopic');

  clubSelect.innerHTML = '';
  currentClubs.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.leader_name ? `${c.name} (${c.leader_name})` : c.name;
    clubSelect.appendChild(opt);
  });

  if (currentAttendanceClubId) {
    clubSelect.value = currentAttendanceClubId;
  }
  if (window.currentUser && window.currentUser.role === 'teacher' && window.currentUser.club_id) {
    clubSelect.value = window.currentUser.club_id;
    clubSelect.disabled = true;
  }

  dateInput.value = new Date().toISOString().split('T')[0];
  topicInput.value = '';
  modal.classList.add('show');
  modal.classList.add('active');
}

function closeAttendanceLessonModal() {
  const modal = document.getElementById('attendanceLessonModal');
  if (modal) {
    modal.classList.remove('show');
    modal.classList.remove('active');
  }
}

async function loadAttendanceResults() {
  if (!currentAttendanceClubId) return;
  const tbody = document.getElementById('attendanceResultsTableBody');
  if (!tbody) return;

  try {
    const res = await apiFetch(`/api/v1/attendance/results?club_id=${currentAttendanceClubId}`);
    if (!res.ok) throw new Error('Natijalarni yuklab bo\'lmadi');
    const data = await res.json();

    document.getElementById('kpiTotalLessonsHeld').innerText = data.total_lessons_held;
    document.getElementById('kpiClubStudentsCount').innerText = data.students_summary.length;

    const avgPct = data.students_summary.length > 0 
      ? Math.round(data.students_summary.reduce((acc, s) => acc + s.attendance_percentage, 0) / data.students_summary.length)
      : 0;
    document.getElementById('kpiAvgAttendancePct').innerText = `${avgPct}%`;

    if (data.students_summary.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">Talabalar mavjud emas.</td></tr>`;
      return;
    }

    tbody.innerHTML = '';
    data.students_summary.forEach((student, idx) => {
      const pct = student.attendance_percentage;
      let colorClass = 'green';
      let badgeClass = 'badge-emerald';
      if (pct < 60) {
        colorClass = 'red';
        badgeClass = 'badge-rose';
      } else if (pct < 75) {
        colorClass = 'amber';
        badgeClass = 'badge-amber';
      }

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="color: var(--text-muted);">${idx + 1}</td>
        <td style="font-weight: 700;">${student.full_name}</td>
        <td style="color: var(--text-secondary);">${student.phone_number || '—'}</td>
        <td><span class="badge badge-indigo">${student.course_level}-kurs</span></td>
        <td style="text-align: center; font-weight: 600;">
          ${student.attended_lessons} / ${student.total_lessons}
        </td>
        <td>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div class="progress-track">
              <div class="progress-fill ${colorClass}" style="width: ${pct}%;"></div>
            </div>
            <span style="font-weight: 700; font-size: 12.5px;">${pct}%</span>
          </div>
        </td>
        <td style="text-align: center;">
          <span class="badge ${badgeClass}">${student.grade_label}</span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--accent-rose); padding: 20px;">${err.message}</td></tr>`;
  }
}

function downloadAttendanceExcel() {
  const isTeacher = window.currentUser && window.currentUser.role === 'teacher';
  const clubId = isTeacher && window.currentUser.club_id ? window.currentUser.club_id : currentAttendanceClubId;
  if (!clubId) {
    showToast('To\'garak tanlanmagan', 'error');
    return;
  }
  window.open(`/api/v1/attendance/export?club_id=${clubId}`, '_blank');
}

async function triggerClubReminderFromAttendance() {
  const isTeacher = window.currentUser && window.currentUser.role === 'teacher';
  const clubId = isTeacher && window.currentUser.club_id ? window.currentUser.club_id : currentAttendanceClubId;
  if (!clubId) {
    showToast('To\'garak tanlanmagan', 'error');
    return;
  }
  const club = currentClubs.find(c => c.id === clubId);
  const clubName = club ? club.name : 'ushbu to\'garak';

  if (!confirm(`“${clubName}” a'zolariga Telegram orqali bugungi mashg‘ulot eslatmasini yuborishni tasdiqlaysizmi?`)) {
    return;
  }

  try {
    const res = await apiFetch(`/api/v1/clubs/${currentAttendanceClubId}/remind`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Eslatma yuborishda xatolik');
    showToast(data.message, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==========================================
// 9. BROADCAST LOGIC
// ==========================================
async function loadBroadcastTab() {
  const select = document.getElementById('broadcastClubSelect');
  if (!select) return;

  if (!currentClubs || currentClubs.length === 0) {
    const res = await apiFetch('/api/v1/clubs');
    if (res.ok) currentClubs = await res.json();
  }

  select.innerHTML = '';
  currentClubs.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.name;
    select.appendChild(opt);
  });

  if (window.currentUser && window.currentUser.role === 'teacher') {
    const radioClub = document.querySelector('input[name="broadcastTarget"][value="club"]');
    if (radioClub) radioClub.checked = true;
    const targetContainer = document.getElementById('broadcastTargetContainer');
    if (targetContainer) targetContainer.style.display = 'none';

    document.getElementById('broadcastClubSelectWrapper').style.display = 'block';
    select.value = window.currentUser.club_id;
    select.disabled = true;
  }

  updateBroadcastPreview();
}

function onBroadcastTargetChange() {
  const isClub = document.querySelector('input[name="broadcastTarget"]:checked')?.value === 'club';
  document.getElementById('broadcastClubSelectWrapper').style.display = isClub ? 'block' : 'none';
  updateBroadcastPreview();
}

function updateBroadcastPreview() {
  const text = document.getElementById('broadcastMessageInput').value;
  const charCount = document.getElementById('broadcastCharCount');
  const previewBody = document.getElementById('tgPreviewBody');
  const previewSender = document.getElementById('tgPreviewSender');
  const previewTime = document.getElementById('tgPreviewTime');

  if (charCount) charCount.innerText = `${text.length} / 4000`;
  if (previewBody) {
    previewBody.innerText = text.trim() ? text : 'Xabar matni bu yerda ko\'rinadi...';
  }

  const isClub = document.querySelector('input[name="broadcastTarget"]:checked')?.value === 'club';
  if (isClub) {
    const select = document.getElementById('broadcastClubSelect');
    const selectedClub = currentClubs.find(c => c.id == select.value);
    previewSender.innerText = selectedClub ? `📢 ${selectedClub.name.toUpperCase()}` : '📢 TO\'GARAK XABARI';
  } else {
    previewSender.innerText = '📢 UNIVERSITET MA\'MURIYATI';
  }

  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  if (previewTime) previewTime.innerText = `${hh}:${mm}`;
}

function insertBroadcastTag(tag) {
  const textarea = document.getElementById('broadcastMessageInput');
  textarea.value = (textarea.value ? textarea.value + '\n' : '') + tag + ' ';
  textarea.focus();
  updateBroadcastPreview();
}

// ==========================================
// 10. TEACHERS MANAGEMENT LOGIC
// ==========================================
let allTeachers = [];

async function loadTeachersTab() {
  const tbody = document.getElementById('teachersTableBody');
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">Yuklanmoqda...</td></tr>`;

  try {
    const res = await apiFetch('/api/v1/teachers');
    if (!res.ok) throw new Error('O\'qituvchilar ro\'yxatini yuklab bo\'lmadi');
    allTeachers = await res.json();

    if (allTeachers.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">Hozircha o'qituvchilar hisoblari yaratilmagan. Yuqoridagi "+ Yangi O'qituvchi Qo'shish" tugmasini bosing.</td></tr>`;
      return;
    }

    tbody.innerHTML = '';
    allTeachers.forEach((teacher, idx) => {
      const createdDate = teacher.created_at ? new Date(teacher.created_at).toLocaleDateString() : '—';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="color: var(--text-muted);">${idx + 1}</td>
        <td style="font-weight: 700;">${teacher.full_name}</td>
        <td><code style="background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px; color: #818CF8;">${teacher.username}</code></td>
        <td><span class="badge badge-indigo">${teacher.club_name || 'To\'garak biriktirilmagan'}</span></td>
        <td>
          <span class="badge ${teacher.is_active ? 'badge-emerald' : 'badge-rose'}">
            ${teacher.is_active ? 'Faol' : 'Nofaol'}
          </span>
        </td>
        <td style="color: var(--text-secondary);">${createdDate}</td>
        <td style="text-align: right;">
          <div style="display: flex; gap: 6px; justify-content: flex-end;">
            <button class="btn btn-secondary" style="font-size: 11px; padding: 4px 10px;" onclick="openTeacherModal(${teacher.id})">
              Tahrirlash
            </button>
            <button class="btn btn-danger" style="font-size: 11px; padding: 4px 10px;" onclick="deleteTeacher(${teacher.id}, '${teacher.full_name}')">
              O'chirish
            </button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--accent-rose); padding: 20px;">${err.message}</td></tr>`;
  }
}

async function openTeacherModal(teacherId = null) {
  const modal = document.getElementById('teacherModal');
  const clubSelect = document.getElementById('teacherFormClubId');

  if (!currentClubs || currentClubs.length === 0) {
    try {
      const res = await apiFetch('/api/v1/clubs');
      if (res.ok) {
        currentClubs = await res.json();
      }
    } catch (e) {
      console.error('To\'garaklar ro\'yxatini yuklab bo\'lmadi:', e);
    }
  }

  clubSelect.innerHTML = '<option value="">Tanlanmagan / To\'garaksiz</option>';
  if (Array.isArray(currentClubs)) {
    currentClubs.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.leader_name ? `${c.name} (${c.leader_name})` : c.name;
      clubSelect.appendChild(opt);
    });
  }

  const pwdInput = document.getElementById('teacherFormPassword');
  const pwdLabel = document.getElementById('teacherFormPasswordLabel');
  const pwdHint = document.getElementById('teacherFormPasswordHint');

  if (teacherId) {
    const teacher = allTeachers.find(t => t.id === teacherId);
    if (!teacher) return;
    document.getElementById('teacherModalTitle').innerText = 'O\'qituvchini Tahrirlash';
    document.getElementById('teacherFormId').value = teacher.id;
    document.getElementById('teacherFormFullName').value = teacher.full_name;
    document.getElementById('teacherFormUsername').value = teacher.username;
    document.getElementById('teacherFormUsername').disabled = true;
    clubSelect.value = teacher.club_id || '';
    pwdInput.value = '';
    pwdInput.required = false;
    pwdLabel.innerText = 'Yangi Parol (ixtiyoriy)';
    pwdHint.innerText = 'Agar parolni o\'zgartirmoqchi bo\'lsangiz, yangi parol kiriting';
    document.getElementById('teacherFormIsActive').checked = teacher.is_active;
  } else {
    document.getElementById('teacherModalTitle').innerText = 'Yangi O\'qituvchi Qo\'shish';
    document.getElementById('teacherFormId').value = '';
    document.getElementById('teacherFormFullName').value = '';
    document.getElementById('teacherFormUsername').value = '';
    document.getElementById('teacherFormUsername').disabled = false;
    clubSelect.value = '';
    pwdInput.value = '';
    pwdInput.required = true;
    pwdLabel.innerText = 'Maxfiy Parol *';
    pwdHint.innerText = 'O\'qituvchi shu login va parol orqali tizimga kiradi (kamida 6 ta belgi)';
    document.getElementById('teacherFormIsActive').checked = true;
  }

  modal.classList.add('show');
  modal.classList.add('active');
}

function closeTeacherModal() {
  const modal = document.getElementById('teacherModal');
  if (modal) {
    modal.classList.remove('show');
    modal.classList.remove('active');
  }
}

async function deleteTeacher(teacherId, teacherName) {
  if (!confirm(`Haqiqatan ham o‘qituvchi “${teacherName}” hisobini o‘chirmoqchimisiz?`)) {
    return;
  }

  try {
    const res = await apiFetch(`/api/v1/teachers/${teacherId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('O\'chirib bo\'lmadi');
    showToast('O\'qituvchi muvaffaqiyatli o\'chirildi', 'success');
    await loadTeachersTab();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

