/* ==========================================================================
   pyHydrogen — Frontend Application Logic
   ========================================================================== */

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const L_LABELS = ["s", "p", "d", "f", "g", "h", "i", "k", "l", "m", "n"];

/** Shared Plotly dark-theme layout defaults. */
const DARK_LAYOUT = {
    paper_bgcolor: "#16213e",
    plot_bgcolor:  "#16213e",
    font: { color: "#e0e0e0", family: "Segoe UI, system-ui, sans-serif", size: 12 },
    margin: { t: 36, r: 16, b: 40, l: 50 },
};

const PLOTLY_CONFIG = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ["lasso2d", "select2d"],
};

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

/** Cache energy-level data so we can highlight without re-fetching. */
let energyData = null;

// ---------------------------------------------------------------------------
// Bootstrap — wait for pywebview bridge to be ready
// ---------------------------------------------------------------------------

window.addEventListener("pywebviewready", async () => {
    document.getElementById("n-select").addEventListener("change", onNChanged);
    document.getElementById("l-select").addEventListener("change", onLChanged);
    document.getElementById("compute-btn").addEventListener("click", onCompute);

    // Load energy-level diagram (independent of n, l, m)
    await loadEnergyLevels();

    // Trigger initial computation for the default state (1, 0, 0)
    await onCompute();
});

// ---------------------------------------------------------------------------
// Quantum-number cascade logic
// ---------------------------------------------------------------------------

async function onNChanged() {
    const n = parseInt(document.getElementById("n-select").value, 10);
    const result = await pywebview.api.getQuantumNumbers(n);
    if (result.error) { setStatus("Error: " + result.error); return; }

    // Rebuild l dropdown
    const lSelect = document.getElementById("l-select");
    lSelect.innerHTML = "";
    result.l_values.forEach((lVal) => {
        const opt = document.createElement("option");
        opt.value = lVal;
        opt.textContent = lVal + " (" + (L_LABELS[lVal] || lVal) + ")";
        lSelect.appendChild(opt);
    });

    // Cascade to m
    await onLChanged();
}

async function onLChanged() {
    const n = parseInt(document.getElementById("n-select").value, 10);
    const l = parseInt(document.getElementById("l-select").value, 10);

    const result = await pywebview.api.getQuantumNumbers(n);
    const mValues = result.m_values_by_l[String(l)] || [0];

    const mSelect = document.getElementById("m-select");
    mSelect.innerHTML = "";
    mValues.forEach((mVal) => {
        const opt = document.createElement("option");
        opt.value = mVal;
        opt.textContent = mVal;
        mSelect.appendChild(opt);
    });

    updateOrbitalLabel();
}

// ---------------------------------------------------------------------------
// Compute handler
// ---------------------------------------------------------------------------

async function onCompute() {
    const n = parseInt(document.getElementById("n-select").value, 10);
    const l = parseInt(document.getElementById("l-select").value, 10);
    const m = parseInt(document.getElementById("m-select").value, 10);

    const btn = document.getElementById("compute-btn");
    btn.disabled = true;
    setStatus("Computing\u2026");

    try {
        // Fire both heavy computations in parallel
        const [isoData, radialData] = await Promise.all([
            pywebview.api.computeIsosurface(n, l, m, 40),
            pywebview.api.computeRadialDistribution(n, l),
        ]);

        if (isoData.error)    throw new Error(isoData.error);
        if (radialData.error) throw new Error(radialData.error);

        renderIsosurface(isoData, n, l, m);
        renderRadialDistribution(radialData, n, l);
        highlightEnergyLevel(n);
        updateOrbitalLabel();
        setStatus("Ready");
    } catch (err) {
        setStatus("Error: " + err.message);
    } finally {
        btn.disabled = false;
    }
}

// ---------------------------------------------------------------------------
// 3-D Isosurface plot
// ---------------------------------------------------------------------------

function renderIsosurface(data, n, l, m) {
    const isomax = data.max_val * 0.15;   // show from 15 % of peak …
    const isomin = data.max_val * 0.0005;  // … down to 0.05 %

    const trace = {
        type: "isosurface",
        x: data.x,
        y: data.y,
        z: data.z,
        value: data.value,
        isomin: isomin,
        isomax: isomax,
        surface: { count: 4, fill: 0.7, show: true },
        caps: { x: { show: false }, y: { show: false }, z: { show: false } },
        colorscale: "Viridis",
        opacity: 0.6,
        showscale: true,
        colorbar: {
            title: { text: "|&psi;|&sup2;", font: { size: 12, color: "#e0e0e0" } },
            tickfont: { color: "#a0a0a0", size: 10 },
            len: 0.6,
        },
    };

    const orbitalName = n + (L_LABELS[l] || l) + (l > 0 ? " (m=" + m + ")" : "");

    const layout = {
        ...DARK_LAYOUT,
        title: { text: "3D Probability Density: " + orbitalName, font: { size: 14 } },
        margin: { t: 40, r: 0, b: 0, l: 0 },
        scene: {
            xaxis: { title: "x (a\u2080)", gridcolor: "#2a2a4a", zerolinecolor: "#3a3a5a", color: "#a0a0a0" },
            yaxis: { title: "y (a\u2080)", gridcolor: "#2a2a4a", zerolinecolor: "#3a3a5a", color: "#a0a0a0" },
            zaxis: { title: "z (a\u2080)", gridcolor: "#2a2a4a", zerolinecolor: "#3a3a5a", color: "#a0a0a0" },
            bgcolor: "#1a1a2e",
            aspectmode: "cube",
        },
    };

    Plotly.react("isosurface-plot", [trace], layout, PLOTLY_CONFIG);
}

// ---------------------------------------------------------------------------
// 2-D Radial Distribution Function
// ---------------------------------------------------------------------------

function renderRadialDistribution(data, n, l) {
    const trace = {
        type: "scatter",
        mode: "lines",
        x: data.r,
        y: data.P_r,
        line: { color: "#e94560", width: 2.5 },
        fill: "tozeroy",
        fillcolor: "rgba(233, 69, 96, 0.15)",
        name: "P(r)",
        hovertemplate: "r = %{x:.2f} a\u2080<br>P(r) = %{y:.4e}<extra></extra>",
    };

    const orbLabel = n + (L_LABELS[l] || l);

    const layout = {
        ...DARK_LAYOUT,
        title: { text: "Radial Distribution \u2014 " + orbLabel, font: { size: 13 } },
        xaxis: {
            title: { text: "r (a\u2080)", font: { size: 12 } },
            gridcolor: "#2a2a4a",
            zerolinecolor: "#3a3a5a",
            color: "#a0a0a0",
        },
        yaxis: {
            title: { text: "r\u00b2|R(r)|\u00b2", font: { size: 12 } },
            gridcolor: "#2a2a4a",
            zerolinecolor: "#3a3a5a",
            color: "#a0a0a0",
        },
        showlegend: false,
    };

    Plotly.react("radial-plot", [trace], layout, PLOTLY_CONFIG);
}

// ---------------------------------------------------------------------------
// Energy-level diagram
// ---------------------------------------------------------------------------

async function loadEnergyLevels() {
    const result = await pywebview.api.getEnergyLevels(6);
    if (result.error) { setStatus("Energy error: " + result.error); return; }
    energyData = result;
    renderEnergyDiagram(1);
}

function renderEnergyDiagram(activeN) {
    if (!energyData) return;

    const traces = [];

    energyData.levels.forEach((level) => {
        const active = level.n === activeN;
        traces.push({
            type: "scatter",
            mode: "lines+text",
            x: [-0.4, 0.4],
            y: [level.energy, level.energy],
            line: { color: active ? "#e94560" : "#607080", width: active ? 3 : 1.5 },
            text: ["", "n=" + level.n + "  " + level.energy.toFixed(2) + " eV"],
            textposition: "middle right",
            textfont: {
                color: active ? "#e94560" : "#a0a0a0",
                size: active ? 12 : 10,
                family: "Consolas, SF Mono, monospace",
            },
            showlegend: false,
            hovertemplate:
                "n = " + level.n +
                "<br>E = " + level.energy.toFixed(4) + " eV" +
                "<br>Degeneracy = " + level.degeneracy +
                "<extra></extra>",
        });
    });

    // Add E = 0 reference line
    traces.push({
        type: "scatter",
        mode: "lines",
        x: [-0.5, 1.4],
        y: [0, 0],
        line: { color: "#2a2a4a", width: 1, dash: "dot" },
        showlegend: false,
        hoverinfo: "skip",
    });

    const layout = {
        ...DARK_LAYOUT,
        title: { text: "Energy Levels", font: { size: 13 } },
        xaxis: { visible: false, range: [-0.6, 1.8] },
        yaxis: {
            title: { text: "Energy (eV)", font: { size: 12 } },
            gridcolor: "#2a2a4a",
            zerolinecolor: "#2a2a4a",
            color: "#a0a0a0",
            range: [-15, 1],
        },
        showlegend: false,
    };

    Plotly.react("energy-plot", traces, layout, PLOTLY_CONFIG);
}

function highlightEnergyLevel(activeN) {
    renderEnergyDiagram(activeN);
}

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

function setStatus(msg) {
    document.getElementById("status-text").textContent = msg;
}

function updateOrbitalLabel() {
    const n = parseInt(document.getElementById("n-select").value, 10);
    const l = parseInt(document.getElementById("l-select").value, 10);
    const m = parseInt(document.getElementById("m-select").value, 10);
    const letter = L_LABELS[l] || String(l);
    document.getElementById("orbital-label").textContent =
        "(" + n + ", " + l + ", " + m + ") \u2014 " + n + letter;
}
