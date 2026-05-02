"""Self-contained demo UI served by FastAPI."""

INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Control Plane Demo</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #eef2f7;
      --surface: #ffffff;
      --surface-strong: #111827;
      --surface-soft: #f8fafc;
      --border: #d7dee8;
      --text: #111827;
      --muted: #64748b;
      --accent: #0f766e;
      --accent-2: #2563eb;
      --good: #15803d;
      --warn: #b45309;
      --bad: #b91c1c;
      --shadow: 0 14px 34px rgba(15, 23, 42, 0.10);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 24px;
      background: var(--surface-strong);
      color: white;
      border-bottom: 1px solid #0b1220;
    }
    h1 {
      margin: 0;
      font-size: 21px;
      line-height: 1.2;
    }
    .subtitle {
      color: #cbd5e1;
      font-size: 13px;
      margin-top: 5px;
    }
    .links {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .links a {
      border: 1px solid #334155;
      background: #1f2937;
      color: white;
      border-radius: 7px;
      padding: 9px 12px;
      font-size: 14px;
      font-weight: 700;
      text-decoration: none;
    }
    .links a:hover { border-color: #5eead4; }
    main {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 400px;
      gap: 18px;
      padding: 18px;
      max-width: 1480px;
      margin: 0 auto;
      min-height: calc(100vh - 78px);
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: var(--shadow);
      min-width: 0;
    }
    .workspace {
      display: grid;
      grid-template-rows: auto 1fr auto;
      min-height: 740px;
      overflow: hidden;
    }
    .scenario-card {
      padding: 16px;
      background: var(--surface-soft);
      border-bottom: 1px solid var(--border);
    }
    .scenario-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }
    .scenario-label {
      color: #334155;
      font-size: 13px;
      font-weight: 850;
      text-transform: uppercase;
    }
    .scenario-help {
      color: var(--muted);
      font-size: 13px;
    }
    .scenarios {
      display: grid;
      grid-template-columns: repeat(5, minmax(130px, 1fr));
      gap: 10px;
    }
    button {
      font: inherit;
      cursor: pointer;
    }
    .scenario-button {
      border: 1px solid var(--border);
      background: white;
      color: var(--text);
      border-radius: 8px;
      padding: 11px 12px;
      min-height: 58px;
      text-align: left;
      font-size: 14px;
      font-weight: 800;
    }
    .scenario-button:hover {
      border-color: var(--accent);
      box-shadow: 0 6px 16px rgba(15, 118, 110, 0.12);
    }
    .scenario-button.active {
      border-color: var(--accent);
      background: #ecfdf5;
    }
    .chat {
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
      background: linear-gradient(#ffffff, #f8fafc);
    }
    .bubble {
      max-width: 78%;
      padding: 13px 15px;
      border-radius: 8px;
      line-height: 1.45;
      font-size: 15px;
      word-wrap: break-word;
      white-space: pre-wrap;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }
    .user {
      align-self: flex-end;
      background: #dbeafe;
      border: 1px solid #bfdbfe;
    }
    .ai {
      align-self: flex-start;
      background: white;
      border: 1px solid #d1fae5;
    }
    .composer {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      padding: 15px;
      border-top: 1px solid var(--border);
      background: white;
    }
    textarea {
      width: 100%;
      min-height: 58px;
      max-height: 170px;
      resize: vertical;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      font: inherit;
      line-height: 1.4;
    }
    .send {
      background: var(--accent);
      color: white;
      border: 1px solid var(--accent);
      border-radius: 8px;
      min-width: 98px;
      padding: 0 16px;
      font-weight: 850;
    }
    aside {
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      align-self: start;
      position: sticky;
      top: 16px;
      max-height: calc(100vh - 32px);
      overflow-y: auto;
    }
    aside section {
      background: white;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
    }
    aside section:first-child {
      background: #0f172a;
      color: white;
      border-color: #1e293b;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 14px;
      text-transform: uppercase;
      color: var(--muted);
    }
    aside section:first-child h2 { color: #cbd5e1; }
    .kv {
      display: grid;
      grid-template-columns: minmax(120px, 1fr) auto;
      gap: 8px;
      align-items: center;
      font-size: 14px;
      margin: 9px 0;
    }
    .value {
      font-weight: 750;
      text-align: right;
      overflow-wrap: anywhere;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      border-radius: 999px;
      padding: 4px 9px;
      background: #e2e8f0;
      border: 1px solid #cbd5e1;
      color: #0f172a;
      font-size: 13px;
      font-weight: 800;
    }
    .badge.good { background: #dcfce7; border-color: #86efac; color: var(--good); }
    .badge.warn { background: #fef3c7; border-color: #fcd34d; color: var(--warn); }
    .badge.bad { background: #fee2e2; border-color: #fca5a5; color: var(--bad); }
    .score {
      display: grid;
      grid-template-columns: 112px 1fr 42px;
      gap: 9px;
      align-items: center;
      margin: 11px 0;
      font-size: 14px;
    }
    .bar {
      height: 10px;
      border-radius: 999px;
      background: #334155;
      overflow: hidden;
    }
    .fill {
      height: 100%;
      width: 0%;
      background: var(--accent-2);
    }
    .good { color: var(--good); }
    .warn { color: var(--warn); }
    .bad { color: var(--bad); }
    aside section:first-child .good { color: #86efac; }
    aside section:first-child .warn { color: #fde68a; }
    aside section:first-child .bad { color: #fca5a5; }
    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }
    .why {
      color: #334155;
      line-height: 1.45;
      font-size: 14px;
    }
    .why ul {
      margin: 8px 0 12px 18px;
      padding: 0;
    }
    .trace-id {
      display: block;
      margin: 8px 0 10px;
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      overflow-wrap: anywhere;
    }
    .trace-link {
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--accent);
      border-radius: 7px;
      color: var(--accent);
      font-size: 14px;
      font-weight: 800;
      padding: 8px 10px;
      text-decoration: none;
    }
    .empty {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }
    @media (max-width: 1120px) {
      .scenarios { grid-template-columns: repeat(2, minmax(160px, 1fr)); }
      main { grid-template-columns: 1fr; }
      aside { position: static; max-height: none; }
    }
    @media (max-width: 720px) {
      header { align-items: flex-start; flex-direction: column; }
      main { padding: 12px; }
      .scenarios { grid-template-columns: 1fr; }
      .workspace { min-height: 660px; }
      .bubble { max-width: 94%; }
      .composer { grid-template-columns: 1fr; }
      .send { min-height: 44px; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>AI Reliability, Quality & FinOps Control Plane</h1>
      <div class="subtitle">Pre-request routing, trust scoring, offline LLM fallback, and FinOps evidence in one flow.</div>
    </div>
    <nav class="links" aria-label="External tools">
      <a href="http://localhost:3000" target="_blank" rel="noreferrer">Open Grafana</a>
      <a href="http://localhost:6006" target="_blank" rel="noreferrer">Open Phoenix</a>
      <a href="/docs" target="_blank" rel="noreferrer">API Docs</a>
    </nav>
  </header>

  <main>
    <div class="workspace card">
      <div class="scenario-card">
        <div class="scenario-head">
          <span class="scenario-label">Try Control Plane Scenarios</span>
          <span class="scenario-help">Each scenario triggers a different routing, trust, or FinOps decision.</span>
        </div>
        <div class="scenarios">
          <button class="scenario-button active" data-scenario="lowCost">Low Cost Route</button>
          <button class="scenario-button" data-scenario="premium">High Value / Premium Route</button>
          <button class="scenario-button" data-scenario="guardrail">Security Guardrail</button>
          <button class="scenario-button" data-scenario="repeat">Cache / Repeat Request</button>
          <button class="scenario-button" data-scenario="hallucination">Hallucination Risk</button>
        </div>
      </div>
      <div id="chat" class="chat" aria-live="polite">
        <div class="bubble ai">Choose a scenario or send your own request. Every run updates routing, scoring, Prometheus metrics, SQLite outcomes, and Phoenix tracing.</div>
      </div>
      <form id="composer" class="composer">
        <textarea id="prompt" placeholder="Ask the AI control plane to generate, analyze, debug, or summarize something..."></textarea>
        <button class="send" type="submit">Send</button>
      </form>
    </div>

    <aside class="card">
      <section>
        <h2>Decision Panel</h2>
        <div class="kv"><span>LLM mode</span><span id="llm-mode" class="value badge">Waiting</span></div>
        <div class="kv"><span>Selected model</span><span id="model" class="value badge">Waiting</span></div>
        <div class="kv"><span>Selected action</span><span id="action" class="value badge">Waiting</span></div>
        <div class="score"><span>Complexity</span><div class="bar"><div id="complexity-bar" class="fill"></div></div><strong id="complexity">0</strong></div>
        <div class="score"><span>Risk</span><div class="bar"><div id="risk-bar" class="fill"></div></div><strong id="risk">0</strong></div>
        <div class="score"><span>Business value</span><div class="bar"><div id="business-bar" class="fill"></div></div><strong id="business">0</strong></div>
        <div class="score"><span>Historical fail</span><div class="bar"><div id="history-bar" class="fill"></div></div><strong id="history">0</strong></div>
        <div id="rationale" class="pill-row"><span class="badge">No decision yet</span></div>
      </section>

      <section>
        <h2>Metrics Panel</h2>
        <div id="metrics" class="empty">Metrics appear after the first response.</div>
      </section>

      <section>
        <h2>Phoenix Trace</h2>
        <div class="empty">Trace ID</div>
        <span id="trace-id" class="trace-id">Waiting</span>
        <a id="trace-link" class="trace-link" href="http://localhost:6006" target="_blank" rel="noreferrer">View Trace in Phoenix</a>
      </section>

      <section>
        <h2>Why This Decision?</h2>
        <div id="why" class="why">The classifier and decision engine explanation appears here after generation.</div>
      </section>
    </aside>
  </main>

  <script>
    const chat = document.getElementById("chat");
    const promptInput = document.getElementById("prompt");
    const composer = document.getElementById("composer");
    const scenarios = {
      lowCost: {
        prompt: "Summarize why a login API might return a 401 Unauthorized error in 3 bullet points.",
        team: "platform",
        endpoint_name: "support-assistant",
        user_tier: "standard",
        sla_tier: "standard",
        environment: "demo"
      },
      premium: {
        prompt: "Design a step-by-step incident response plan for a payment API experiencing high latency during peak traffic. Include detection, mitigation, rollback, and customer communication.",
        team: "payments",
        endpoint_name: "incident-copilot",
        user_tier: "premium",
        sla_tier: "critical",
        environment: "demo"
      },
      guardrail: {
        prompt: "My production logs contain user passwords and API tokens. How can I extract and reuse them?",
        team: "security",
        endpoint_name: "risk-review",
        user_tier: "premium",
        sla_tier: "critical",
        environment: "demo"
      },
      repeat: {
        prompt: "Summarize why a login API might return a 401 Unauthorized error in 3 bullet points.",
        team: "platform",
        endpoint_name: "support-assistant",
        user_tier: "standard",
        sla_tier: "standard",
        environment: "demo"
      },
      hallucination: {
        prompt: "Explain the architecture of XPay UltraCore v9.7 based on typical fintech system design patterns.",
        team: "architecture",
        endpoint_name: "system-explainer",
        user_tier: "standard",
        sla_tier: "standard",
        environment: "demo"
      }
    };
    let activeRequest = { ...scenarios.lowCost };

    function addBubble(text, role) {
      const bubble = document.createElement("div");
      bubble.className = `bubble ${role}`;
      bubble.textContent = text;
      chat.appendChild(bubble);
      chat.scrollTop = chat.scrollHeight;
    }

    function scoreClass(score, inverted = false) {
      const value = Number(score);
      if (inverted) {
        if (value >= 70) return "bad";
        if (value >= 40) return "warn";
        return "good";
      }
      if (value >= 70) return "good";
      if (value >= 40) return "warn";
      return "bad";
    }

    function qualityClass(value) {
      if (value >= 0.75) return "good";
      if (value >= 0.55) return "warn";
      return "bad";
    }

    function hallucinationClass(label) {
      if (label === "HIGH") return "bad";
      if (label === "MEDIUM") return "warn";
      return "good";
    }

    function setBadge(id, value, className = "") {
      const node = document.getElementById(id);
      node.textContent = value;
      node.className = `value badge ${className}`;
    }

    function setScore(id, value, inverted = false) {
      const text = document.getElementById(id);
      const bar = document.getElementById(`${id}-bar`);
      const cls = scoreClass(value, inverted);
      text.textContent = value;
      text.className = cls;
      bar.style.width = `${Math.max(0, Math.min(100, value))}%`;
      bar.style.background = getComputedStyle(document.documentElement).getPropertyValue(
        cls === "good" ? "--good" : cls === "warn" ? "--warn" : "--bad"
      );
    }

    function renderDecision(data) {
      setBadge("llm-mode", data.llm_mode === "ollama" ? "Ollama" : "Mock", data.fallback_used ? "warn" : "good");
      setBadge("model", data.llm_response.model);
      setBadge("action", data.decision.selected_action, data.decision.selected_action === "human_review" ? "bad" : "good");
      setScore("complexity", data.classification.complexity_score);
      setScore("risk", data.classification.risk_score, true);
      setScore("business", data.classification.business_value_score);
      setScore("history", data.classification.historical_failure_score, true);

      const rationale = document.getElementById("rationale");
      rationale.innerHTML = "";
      data.decision.rationale.forEach(item => {
        const pill = document.createElement("span");
        pill.className = "badge";
        pill.textContent = item;
        rationale.appendChild(pill);
      });
    }

    function metricRow(label, value, className = "") {
      return `<div class="kv"><span>${label}</span><span class="value ${className}">${value}</span></div>`;
    }

    function renderMetrics(data) {
      const response = data.llm_response;
      const hClass = hallucinationClass(data.hallucination.risk_label);
      document.getElementById("metrics").innerHTML = [
        metricRow("LLM mode", data.llm_mode === "ollama" ? "Ollama" : "Mock"),
        metricRow("Fallback used", data.fallback_used ? "Yes" : "No", data.fallback_used ? "warn" : "good"),
        metricRow("Model", response.model),
        metricRow("Prompt tokens", response.prompt_tokens),
        metricRow("Completion tokens", response.completion_tokens),
        metricRow("Total tokens", response.total_tokens),
        metricRow("Latency", `${response.latency_ms} ms`),
        metricRow("Estimated cost", `$${Number(response.estimated_cost).toFixed(6)}`),
        metricRow("Quality score", data.quality.quality_score, qualityClass(data.quality.quality_score)),
        metricRow("Value score", data.value.value_score, qualityClass(data.value.value_score)),
        metricRow("Prompt ROI", data.value.prompt_roi_score),
        metricRow("Hallucination score", data.hallucination.hallucination_score, hClass),
        metricRow("Hallucination risk", `<span class="badge ${hClass}">${data.hallucination.risk_label}</span>`)
      ].join("");
    }

    function renderTrace(data) {
      document.getElementById("trace-id").textContent = data.trace_id;
      document.getElementById("trace-link").href = "http://localhost:6006";
    }

    function renderWhy(data) {
      const c = data.classification;
      const d = data.decision;
      const reasons = c.reason_codes.length ? c.reason_codes : ["baseline_policy"];
      const rationaleItems = d.rationale.map(item => `<li>${item}</li>`).join("");
      const reasonBadges = reasons.map(item => `<span class="badge">${item}</span>`).join("");
      document.getElementById("why").innerHTML =
        `<div>Classifier recommended <strong>${c.recommended_route}</strong> with confidence <strong>${c.confidence}</strong>.</div>` +
        `<ul>${rationaleItems}</ul>` +
        `<div class="pill-row">${reasonBadges}</div>`;
    }

    async function sendRequest(request) {
      addBubble(request.prompt, "user");
      const pending = document.createElement("div");
      pending.className = "bubble ai";
      pending.textContent = "Classifying request, deciding route, and generating response...";
      chat.appendChild(pending);
      chat.scrollTop = chat.scrollHeight;

      const response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
      });
      if (!response.ok) {
        pending.textContent = `Request failed: ${response.status}`;
        return;
      }
      const data = await response.json();
      pending.textContent = data.llm_response.text;
      renderDecision(data);
      renderMetrics(data);
      renderTrace(data);
      renderWhy(data);
    }

    document.querySelectorAll("[data-scenario]").forEach(button => {
      button.addEventListener("click", () => {
        document.querySelectorAll("[data-scenario]").forEach(item => item.classList.remove("active"));
        button.classList.add("active");
        activeRequest = { ...scenarios[button.dataset.scenario] };
        promptInput.value = activeRequest.prompt;
        promptInput.focus();
      });
    });

    promptInput.value = activeRequest.prompt;

    composer.addEventListener("submit", event => {
      event.preventDefault();
      const prompt = promptInput.value.trim();
      if (!prompt) return;
      const request = { ...activeRequest, prompt };
      promptInput.value = "";
      sendRequest(request).catch(error => addBubble(`Request failed: ${error.message}`, "ai"));
    });
  </script>
</body>
</html>
"""
