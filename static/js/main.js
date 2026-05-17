// Toast notification
function showToast(msg, type = 'success') {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.className = 'toast toast--' + type;
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => toast.classList.remove('show'), 2800);
}

// AJAX check-in buttons
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.checkin-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      btn.disabled = true;
      btn.textContent = '...';
      try {
        const res = await fetch(`/habits/${id}/checkin`, { method: 'POST' });
        const data = await res.json();

        if (data.status === 'ok') {
          // Update button
          btn.textContent = 'Done Today \u2713';
          btn.className = 'btn btn-success btn-sm';
          btn.disabled = true;

          // Update streak display
          const streakEl = document.getElementById('streak-' + id);
          if (streakEl) streakEl.textContent = data.streak;

          // Update card border
          const card = document.getElementById('card-' + id);
          if (card) card.classList.add('habit-card--done');

          // Update summary count
          const doneEl = document.querySelector('.stat-card--green .stat-value');
          if (doneEl) doneEl.textContent = parseInt(doneEl.textContent || 0) + 1;

          showToast('Streak: ' + data.streak + ' day' + (data.streak !== 1 ? 's' : '') + '!', 'success');
        } else {
          btn.textContent = 'Done Today \u2713';
          btn.className = 'btn btn-success btn-sm';
          btn.disabled = true;
          showToast(data.message, 'info');
        }
      } catch (e) {
        btn.textContent = 'Check In';
        btn.disabled = false;
        showToast('Something went wrong.', 'error');
      }
    });
  });
});
