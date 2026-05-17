document.addEventListener('DOMContentLoaded', () => {

  // ── HEAT MAP ──
  const heatmapEl = document.getElementById('heatmap');
  if (heatmapEl && typeof heatmapData !== 'undefined') {
    Object.entries(heatmapData).forEach(([dateStr, val]) => {
      const cell = document.createElement('div');
      cell.className = 'heatmap-cell' + (val ? ' heatmap-cell--done' : '');
      cell.title = dateStr;
      heatmapEl.appendChild(cell);
    });
  }

  // ── WEEKLY BAR CHART ──
  const canvas = document.getElementById('weeklyChart');
  if (canvas && typeof weeklyData !== 'undefined') {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: days,
        datasets: [{
          label: 'Completed',
          data: weeklyData,
          backgroundColor: weeklyData.map(v => v ? '#22c55e' : '#e2e8f0'),
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ctx.raw ? 'Done' : 'Missed'
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true, max: 1,
            ticks: { display: false },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#64748b', font: { size: 13 } }
          }
        }
      }
    });
  }
});
