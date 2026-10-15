// Global Chart Instances
let riskChart = null;
let modelChart = null;

document.addEventListener('DOMContentLoaded', () => {
  // Setup explicit tab navigation handler
  setupTabNavigation();

  // Sync range inputs with number inputs
  setupInputSync();

  // Load initial data
  loadDashboardData();
  loadModelComparison();
  loadHistoryData();

  // Form submission for prediction
  const predictForm = document.getElementById('predictionForm');
  if (predictForm) {
    predictForm.addEventListener('submit', handlePredictionSubmit);
  }

  // Batch CSV upload handler
  const batchForm = document.getElementById('batchForm');
  if (batchForm) {
    batchForm.addEventListener('submit', handleBatchUpload);
  }
});

function setupTabNavigation() {
  const tabElList = document.querySelectorAll('#mainTab button[data-bs-toggle="tab"]');
  tabElList.forEach(tabEl => {
    tabEl.addEventListener('click', (e) => {
      e.preventDefault();
      
      const targetId = tabEl.getAttribute('data-bs-target');

      if (window.bootstrap && window.bootstrap.Tab) {
        const tab = window.bootstrap.Tab.getOrCreateInstance(tabEl);
        tab.show();
      } else {
        // Fallback tab toggling
        document.querySelectorAll('#mainTab .nav-link').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('#mainTabContent .tab-pane').forEach(pane => pane.classList.remove('show', 'active'));
        
        tabEl.classList.add('active');
        const targetPane = document.querySelector(targetId);
        if (targetPane) targetPane.classList.add('show', 'active');
      }

      // Refresh tab data
      if (targetId === '#analytics-pane') {
        loadDashboardData();
        loadModelComparison();
      } else if (targetId === '#history-pane') {
        loadHistoryData();
      }
    });
  });
}

function setupInputSync() {
  const syncPairs = [
    { range: 'pregnanciesRange', num: 'pregnancies' },
    { range: 'glucoseRange', num: 'glucose' },
    { range: 'bpRange', num: 'blood_pressure' },
    { range: 'skinRange', num: 'skin_thickness' },
    { range: 'insulinRange', num: 'insulin' },
    { range: 'bmiRange', num: 'bmi' },
    { range: 'dpfRange', num: 'dpf' },
    { range: 'ageRange', num: 'age' }
  ];

  syncPairs.forEach(pair => {
    const rangeEl = document.getElementById(pair.range);
    const numEl = document.getElementById(pair.num);

    if (rangeEl && numEl) {
      rangeEl.addEventListener('input', (e) => numEl.value = e.target.value);
      numEl.addEventListener('input', (e) => rangeEl.value = e.target.value);
    }
  });
}

async function handlePredictionSubmit(e) {
  e.preventDefault();
  const submitBtn = document.getElementById('btnSubmitPredict');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Analyzing Health Metrics...';

  const formData = {
    patient_name: document.getElementById('patient_name').value.trim() || "Anonymous Patient",
    pregnancies: parseInt(document.getElementById('pregnancies').value),
    glucose: parseFloat(document.getElementById('glucose').value),
    blood_pressure: parseFloat(document.getElementById('blood_pressure').value),
    skin_thickness: parseFloat(document.getElementById('skin_thickness').value),
    insulin: parseFloat(document.getElementById('insulin').value),
    bmi: parseFloat(document.getElementById('bmi').value),
    dpf: parseFloat(document.getElementById('dpf').value),
    age: parseInt(document.getElementById('age').value)
  };

  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const data = await response.json();
    displayPredictionResults(data);

    // Refresh dashboard stats & history
    loadDashboardData();
    loadHistoryData();

  } catch (error) {
    alert("Error performing prediction: " + error.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-microchip me-2"></i> Calculate Risk Score';
  }
}

function displayPredictionResults(data) {
  const resultCard = document.getElementById('resultCard');
  resultCard.classList.remove('d-none');
  resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Update Percentage Gauge Text
  document.getElementById('probValue').innerText = `${data.probability}%`;
  
  const riskBadge = document.getElementById('riskBadge');
  const riskClass = data.risk_level.toLowerCase().split(' ')[0];
  riskBadge.className = `badge-risk ${riskClass}`;
  riskBadge.innerHTML = `<i class="fas ${riskClass === 'high' ? 'fa-exclamation-triangle' : (riskClass === 'moderate' ? 'fa-exclamation-circle' : 'fa-check-circle')}"></i> ${data.risk_level}`;

  document.getElementById('resultPatientName').innerText = data.patient_name;
  document.getElementById('resultModelUsed').innerText = `Model: ${data.model_used}`;

  // SVG Gauge Circle Update
  const strokeDash = (data.probability / 100) * 440; // 2 * pi * r = 2 * 3.14159 * 70 = 440
  const gaugeCircle = document.getElementById('gaugeCircleProgress');
  if (gaugeCircle) {
    gaugeCircle.style.strokeDasharray = `${strokeDash}, 440`;
    if (riskClass === 'high') gaugeCircle.style.stroke = '#ef4444';
    else if (riskClass === 'moderate') gaugeCircle.style.stroke = '#f59e0b';
    else gaugeCircle.style.stroke = '#10b981';
  }

  // Risk Factors list
  const factorsContainer = document.getElementById('riskFactorsList');
  factorsContainer.innerHTML = '';
  if (data.risk_factors && data.risk_factors.length > 0) {
    data.risk_factors.forEach(f => {
      const li = document.createElement('li');
      li.className = 'text-warning mb-1';
      li.innerHTML = `<i class="fas fa-shield-alt me-2"></i> ${f}`;
      factorsContainer.appendChild(li);
    });
  } else {
    factorsContainer.innerHTML = '<li class="text-success"><i class="fas fa-check me-2"></i> No high risk factors identified.</li>';
  }

  // Recommendations list
  const recContainer = document.getElementById('recommendationsList');
  recContainer.innerHTML = '';
  if (data.recommendations && data.recommendations.length > 0) {
    data.recommendations.forEach(r => {
      const div = document.createElement('div');
      div.className = 'rec-item';
      div.innerHTML = `<i class="fas fa-user-md text-info me-2"></i> ${r}`;
      recContainer.appendChild(div);
    });
  }
}

async function loadDashboardData() {
  try {
    const res = await fetch('/api/dashboard');
    const json = await res.json();
    if (json.status === 'success') {
      const s = json.stats;
      document.getElementById('statTotalPreds').innerText = s.total_predictions;
      document.getElementById('statHighRiskPct').innerText = `${s.high_risk_percentage}%`;
      document.getElementById('statAvgGlucose').innerText = s.avg_glucose;
      document.getElementById('statAvgBmi').innerText = s.avg_bmi;

      renderRiskDoughnut(s.risk_breakdown);
    }
  } catch (err) {
    console.error("Dashboard fetch error:", err);
  }
}

function renderRiskDoughnut(breakdown) {
  const ctx = document.getElementById('riskDoughnutChart');
  if (!ctx) return;

  const labels = Object.keys(breakdown);
  const data = Object.values(breakdown);

  if (riskChart) riskChart.destroy();

  riskChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Outfit' } } }
      },
      cutout: '70%'
    }
  });
}

async function loadModelComparison() {
  try {
    const res = await fetch('/api/model-comparison');
    const json = await res.json();
    if (json.status === 'success') {
      const comp = json.comparison;
      const models = Object.keys(comp);
      const accs = models.map(m => comp[m].accuracy);
      const f1s = models.map(m => comp[m].f1_score);
      const rocs = models.map(m => comp[m].roc_auc);

      renderModelChart(models, accs, f1s, rocs);
    }
  } catch (err) {
    console.error("Model comp fetch error:", err);
  }
}

function renderModelChart(labels, accs, f1s, rocs) {
  const ctx = document.getElementById('modelComparisonChart');
  if (!ctx) return;

  if (modelChart) modelChart.destroy();

  modelChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        { label: 'Accuracy', data: accs, backgroundColor: '#3b82f6', borderRadius: 6 },
        { label: 'F1-Score', data: f1s, backgroundColor: '#10b981', borderRadius: 6 },
        { label: 'ROC-AUC', data: rocs, backgroundColor: '#8b5cf6', borderRadius: 6 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0.5, max: 1.0, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
      },
      plugins: {
        legend: { position: 'top', labels: { color: '#94a3b8' } }
      }
    }
  });
}

async function loadHistoryData() {
  try {
    const res = await fetch('/api/history');
    const json = await res.json();
    if (json.status === 'success') {
      const tbody = document.getElementById('historyTableBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      json.data.forEach(row => {
        const tr = document.createElement('tr');
        const rClass = row.risk_level.toLowerCase().split(' ')[0];

        tr.innerHTML = `
          <td>#${row.id}</td>
          <td class="fw-bold">${escapeHtml(row.patient_name)}</td>
          <td>${row.age} yrs</td>
          <td>${row.glucose} mg/dL</td>
          <td>${row.bmi}</td>
          <td><span class="badge-risk ${rClass}">${row.risk_level} (${(row.probability * 100).toFixed(1)}%)</span></td>
          <td><small class="text-muted">${row.timestamp}</small></td>
          <td>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteHistoryRecord(${row.id})">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("History fetch error:", err);
  }
}

async function deleteHistoryRecord(id) {
  if (!confirm(`Are you sure you want to delete prediction record #${id}?`)) return;

  try {
    const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
    if (res.ok) {
      loadHistoryData();
      loadDashboardData();
    }
  } catch (err) {
    alert("Failed to delete record: " + err.message);
  }
}

async function clearAllRecords() {
  if (!confirm('Are you sure you want to clear ALL prediction records? This cannot be undone.')) return;

  const btn = document.getElementById('btnClearAll');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Clearing...'; }

  try {
    const res = await fetch('/api/history/all', { method: 'DELETE' });
    if (res.ok) {
      loadHistoryData();
      loadDashboardData();
    } else {
      alert('Failed to clear records.');
    }
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-trash-alt me-2"></i> Clear All Records'; }
  }
}

async function handleBatchUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('csvFileInput');
  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please select a CSV file to upload.");
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  const statusDiv = document.getElementById('batchStatus');
  statusDiv.innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div> Processing dataset batch...';

  try {
    const res = await fetch('/api/batch-predict', {
      method: 'POST',
      body: formData
    });

    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Batch processing failed.");

    statusDiv.innerHTML = `<div class="alert alert-success mt-3"><i class="fas fa-check-circle me-2"></i> Processed ${json.total_processed} records successfully! Saved to history.</div>`;

    loadDashboardData();
    loadHistoryData();

  } catch (err) {
    statusDiv.innerHTML = `<div class="alert alert-danger mt-3"><i class="fas fa-exclamation-triangle me-2"></i> ${err.message}</div>`;
  }
}

function exportHistoryCSV() {
  fetch('/api/history')
    .then(res => res.json())
    .then(json => {
      if (!json.data || json.data.length === 0) {
        alert("No history records available to export.");
        return;
      }
      
      const keys = Object.keys(json.data[0]);
      let csvContent = keys.join(',') + '\n';
      
      json.data.forEach(row => {
        const values = keys.map(k => `"${row[k]}"`);
        csvContent += values.join(',') + '\n';
      });

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', `diabetes_predictions_export_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
