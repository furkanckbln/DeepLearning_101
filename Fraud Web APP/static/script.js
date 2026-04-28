// Generate V1–V28 input fields
(function buildVFields() {
    const grid = document.getElementById('v-fields');
    for (let i = 1; i <= 28; i++) {
        grid.insertAdjacentHTML('beforeend', `
            <div class="field">
                <label for="V${i}">V${i}</label>
                <input type="number" id="V${i}" name="V${i}" step="any" placeholder="0.0" required>
            </div>
        `);
    }
})();

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.remove('hidden');
    setTimeout(() => t.classList.add('hidden'), 3000);
}

async function loadSample(label) {
    try {
        const res = await fetch(`/sample/${label}`);
        if (!res.ok) throw new Error();
        const data = await res.json();
        Object.entries(data).forEach(([key, val]) => {
            const el = document.getElementById(key);
            if (el) el.value = parseFloat(val.toFixed(6));
        });
        showToast(label === 1 ? 'Sahte işlem örneği yüklendi.' : 'Normal işlem örneği yüklendi.');
    } catch {
        showToast('Örnek yüklenirken hata oluştu.');
    }
}

async function runPredict(event) {
    event.preventDefault();

    const btn = document.getElementById('submit-btn');
    btn.disabled = true;
    btn.querySelector('.btn-text').classList.add('hidden');
    btn.querySelector('.btn-loading').classList.remove('hidden');

    const inputs = document.querySelectorAll('#form input[type="number"]');
    const body = {};
    inputs.forEach(input => { body[input.name] = parseFloat(input.value); });

    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error();
        const data = await res.json();
        showResult(data);
    } catch {
        showToast('Tahmin sırasında hata oluştu. Sunucuyu kontrol edin.');
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').classList.remove('hidden');
        btn.querySelector('.btn-loading').classList.add('hidden');
    }
}

function showResult(data) {
    const resultCard = document.getElementById('result');
    const header     = document.getElementById('result-header');
    const icon       = document.getElementById('result-icon');
    const label      = document.getElementById('result-label');
    const probText   = document.getElementById('prob-text');
    const probBar    = document.getElementById('prob-bar');

    const isFraud = data.is_fraud;
    const pct = (data.probability * 100).toFixed(2);

    header.className   = `result-header ${isFraud ? 'fraud' : 'normal'}`;
    icon.textContent   = isFraud ? '⚠️' : '✅';
    label.textContent  = isFraud ? 'SAHTE İŞLEM' : 'NORMAL İŞLEM';
    probText.textContent = `${pct}%`;

    probBar.style.width = '0%';
    probBar.className   = `prob-bar ${isFraud ? 'fraud' : 'normal'}`;

    resultCard.classList.remove('hidden');

    // Trigger bar animation after paint
    requestAnimationFrame(() => requestAnimationFrame(() => {
        probBar.style.width = `${pct}%`;
    }));

    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
