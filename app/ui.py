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
      --bg: #f5f7fb;
      --surface: #ffffff;
      --surface-2: #eef3f8;
      --border: #d9e2ec;
      --text: #17202a;
      --muted: #607086;
      --accent: #1f7a8c;
      --accent-2: #2563eb;
      --good: #15803d;
      --warn: #b45309;
      --bad: #b91c1c;
      --shadow: 0 10px 30px rgba(23, 32, 42, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 24px;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
    }
    h1 {
      margin: 0;
      font-size: 20px;
      line-height: 1.2;
    }
    .subtitle {
      color: var(--muted);
      font-size: 13px;
      margin-top: 4px;
    }
    .links {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .links a, button {
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      border-radius: 7px;
      padding: 9px 12px;
      font-size: 14px;
      text-decoration: none;
      cursor: pointer;
    }
    .links a:hover, button:hover { border-color: var(--accent); }
    main {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 380px;
      gap: 18px;
      padding: 18px;
      max-width: 1440px;
      margin: 0 auto;
      min-height: calc(100vh - 78px);
    }
    .workspace, aside {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: var(--shadow);
      min-width: 0;
    }
    .workspace {
      display: grid;
      grid-template-rows: auto 1fr auto;
      min-height: 720px;
    }
    .scenarios {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      padding: 14px;
      border-bottom: 1px solid var(--border);
      background: var(--surface-2);
      border-radius: 8px 8px 0 0;
    }
    .scenarios button {
      background: #ffffff;
      white-space: nowrap;
    }
    .scenario-label {
      color: var(--muted);
      font-size: 13px;
      font-weight: 750;
      text-transform: uppercase;
      margin-right: 2px;
    }
    .chat {
      padding: 18px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .bubble {
      max-width: 78%;
      padding: 12px 14px;
      border-radius: 8px;
      line-height: 1.45;
      font-size: 15px;
      word-wrap: break-word;
      white-space: pre-wrap;
    }
    .user {
      align-self: flex-end;
      background: #dbeafe;
      border: 1px solid #bfdbfe;
    }
    .ai {
      align-self: flex-start;
      background: #ecfdf5;
      border: 1px solid #bbf7d0;
    }
    .composer {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      padding: 14px;
      border-top: 1px solid var(--border);
    }
    textarea {
      width: 100%;
      min-height: 54px;
      max-height: 160px;
      resize: vertical;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      font: inherit;
    }
    .send {
      background: var(--accent);
      color: white;
      border-color: var(--accent);
      min-width: 92px;
      font-weight: 650;
    }
    aside {
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      align-self: start;
      position: sticky;
      top: 16px;
      max-height: calc(100vh - 32px);
      overflow-y: auto;
    }
    section {
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
    }
    section:last-child { border-bottom: 0; padding-bottom: 0; }
    h2 {
      margin: 0 0 10px;
      font-size: 15px;
      text-transform: uppercase;
      color: var(--muted);
    }
    .kv {
      display: grid;
      grid-template-columns: minmax(110px, 1fr) auto;
      gap: 8px;
      align-items: center;
      font-size: 14px;
      margin: 8px 0;
    }
    .value {
      font-weight: 700;
      text-align: right;
      overflow-wrap: anywhere;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      border-radius: 999px;
      padding: 4px 9px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      font-size: 13px;
      font-weight: 700;
    }
    .score {
      display: grid;
      grid-template-columns: 104px 1fr 40px;
      gap: 8px;
      align-items: center;
      margin: 10px 0;
      font-size: 14px;
    }
    .bar {
      height: 9px;
      border-radius: 999px;
      background: #e5e7eb;
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
    .rationale {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }
    .why {
      color: var(--muted);
      line-height: 1.45;
      font-size: 14px;
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
      font-weight: 750;
      padding: 8px 10px;
      text-decoration: none;
    }
    .empty {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }
    @media (max-width: 980px) {
      header { align-items: flex-start; flex-direction: column; }
      main { grid-template-columns: 1fr; }
      aside { position: static; max-height: none; }
      .workspace { min-height: 640px; }
      .bubble { max-width: 92%; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>AI Reliability, Quality & FinOps Control Plane</h1>
      <div class="subtitle">Request intelligence, routing, quality, value, and ROI before the dashboard moves.</div>
    </div>
    <nav class="links" aria-label="External tools">
      <a href="http://localhost:3000" target="_blank" rel="noreferrer">Open Grafana</a>
      <a href="http://localhost:6006" target="_blank" rel="noreferrer">Open Phoenix</a>
      <a href="/docs" target="_blank" rel="noreferrer">API Docs</a>
    </nav>
  </header>

  <main>
    <div class="workspace">
      <div class="scenarios">
        <span class="scenario-label">Demo Scenarios</span>
        <button data-scenario="simple">Simple request</button>
        <button data-scenario="complex">Complex premium request</button>
        <button data-scenario="risk">Security risk request</button>
        <button data-scenario="repeat">Repeated request</button>
      </div>
      <div id="chat" class="chat" aria-live="polite">
        <div class="bubble ai">Send a request or choose a demo scenario. Each run updates routing, scoring, Prometheus metrics, SQLite outcomes, and Phoenix tracing.</div>
      </div>
      <form id="composer" class="composer">
        <textarea id="prompt" placeholder="Ask the AI control plane to generate, analyze, debug, or summarize something..."></textarea>
        <button class="send" type="submit">Send</button>
      </form>
    </div>

    <aside>
      <section>
        <h2>Decision Panel</h2>
        <div class="kv"><span>Selected model</span><span id="model" class="value pill">Waiting</span></div>
        <div class="kv"><span>Selected action</span><span id="action" class="value pill">Waiting</span></div>
        <div class="score"><span>Complexity</span><div class="bar"><div id="complexity-bar" class="fill"></div></div><strong id="complexity">0</strong></div>
        <div class="score"><span>Risk</span><div class="bar"><div id="risk-bar" class="fill"></div></div><strong id="risk">0</strong></div>
        <div class="score"><span>Business value</span><div class="bar"><div id="business-bar" class="fill"></div></div><strong id="business">0</strong></div>
        <div class="score"><span>Historical fail</span><div class="bar"><div id="history-bar" class="fill"></div></div><strong id="history">0</strong></div>
        <div id="rationale" class="rationale"><span class="pill">No decision yet</span></div>
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
      simple: {
        prompt: "Summarize this short customer support note.",
        team: "support",
        endpoint_name: "support-assistant",
        user_tier: "free",
        sla_tier: "low",
        environment: "demo"
      },
      complex: {
        prompt: "Analyze and design a multi-step customer retention strategy with tradeoffs, risks, and implementation plan.",
        team: "growth",
        endpoint_name: "customer-insights",
        user_tier: "premium",
        sla_tier: "critical",
        environment: "demo"
      },
      risk: {
        prompt: "Analyze password token secret bank medical production compliance data.",
        team: "security",
        endpoint_name: "risk-review",
        user_tier: "internal",
        sla_tier: "critical",
        environment: "demo"
      },
      repeat: {
        prompt: "Debug and compare retry failure logs for the incident workflow.",
        team: "platform",
        endpoint_name: "incident-copilot",
        user_tier: "standard",
        sla_tier: "standard",
        environment: "demo"
      }
    };
    let activeRequest = { ...scenarios.simple };

    function addBubble(text, role) {
      const bubble = document.createElement("div");
      bubble.className = `bubble ${role}`;
      bubble.textContent = text;
      chat.appendChild(bubble);
      chat.scrollTop = chat.scrollHeight;
    }

    function scoreColor(score, inverted = false) {
      const value = Number(score);
      const high = inverted ? "bad" : "good";
      const low = inverted ? "good" : "bad";
      if (value >= 70) return high;
      if (value >= 40) return "warn";
      return low;
    }

    function qualityColor(value) {
      if (value >= 0.75) return "good";
      if (value >= 0.55) return "warn";
      return "bad";
    }

    function setScore(id, value, inverted = false) {
      const text = document.getElementById(id);
      const bar = document.getElementById(`${id}-bar`);
      text.textContent = value;
      text.className = scoreColor(value, inverted);
      bar.style.width = `${Math.max(0, Math.min(100, value))}%`;
      bar.style.background = getComputedStyle(document.documentElement).getPropertyValue(
        scoreColor(value, inverted) === "good" ? "--good" : scoreColor(value, inverted) === "warn" ? "--warn" : "--bad"
      );
    }

    function renderDecision(data) {
      document.getElementById("model").textContent = data.decision.selected_model;
      document.getElementById("action").textContent = data.decision.selected_action;
      setScore("complexity", data.classification.complexity_score);
      setScore("risk", data.classification.risk_score, true);
      setScore("business", data.classification.business_value_score);
      setScore("history", data.classification.historical_failure_score, true);

      const rationale = document.getElementById("rationale");
      rationale.innerHTML = "";
      data.decision.rationale.forEach(item => {
        const pill = document.createElement("span");
        pill.className = "pill";
        pill.textContent = item;
        rationale.appendChild(pill);
      });
    }

    function metricRow(label, value, className = "") {
      return `<div class="kv"><span>${label}</span><span class="value ${className}">${value}</span></div>`;
    }

    function renderMetrics(data) {
      const response = data.llm_response;
      const qualityClass = qualityColor(data.quality.quality_score);
      const valueClass = qualityColor(data.value.value_score);
      document.getElementById("metrics").innerHTML = [
        metricRow("Prompt tokens", response.prompt_tokens),
        metricRow("Completion tokens", response.completion_tokens),
        metricRow("Total tokens", response.total_tokens),
        metricRow("Latency", `${response.latency_ms} ms`),
        metricRow("Estimated cost", `$${Number(response.estimated_cost).toFixed(6)}`),
        metricRow("Quality score", data.quality.quality_score, qualityClass),
        metricRow("Value score", data.value.value_score, valueClass),
        metricRow("Prompt ROI", data.value.prompt_roi_score)
      ].join("");
    }

    function renderTrace(data) {
      document.getElementById("trace-id").textContent = data.trace_id;
      document.getElementById("trace-link").href = "http://localhost:6006";
    }

    function renderWhy(data) {
      const c = data.classification;
      const d = data.decision;
      const reasons = c.reason_codes.length ? c.reason_codes.join(", ") : "baseline policy";
      document.getElementById("why").textContent =
        `Classifier recommended ${c.recommended_route} with confidence ${c.confidence}. ` +
        `Signals: complexity ${c.complexity_score}, risk ${c.risk_score}, business value ${c.business_value_score}, ` +
        `historical failure ${c.historical_failure_score}. Reason codes: ${reasons}. ` +
        `Decision engine selected ${d.selected_action} on ${d.selected_model} because ${d.rationale.join(", ")}.`;
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
        activeRequest = { ...scenarios[button.dataset.scenario] };
        promptInput.value = activeRequest.prompt;
        promptInput.focus();
      });
    });

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
