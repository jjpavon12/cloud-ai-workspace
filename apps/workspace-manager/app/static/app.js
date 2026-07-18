const API_BASE = "/workspace-api";

const MODE_DATA = {
  copilot: {
    label: "Copilot",
    icon: "C",
    description:
      "Ollama utiliza la GPU para asistir al desarrollo desde Code Server.",
  },

  train: {
    label: "Train",
    icon: "T",
    description:
      "Jupyter tiene disponible la GPU para ejecutar notebooks y entrenamientos.",
  },

  stopped: {
    label: "Stopped",
    icon: "S",
    description:
      "Ollama y Jupyter están detenidos. La GPU está libre.",
  },

  transition: {
    label: "Transition",
    icon: "…",
    description:
      "La plataforma se encuentra cambiando de workspace.",
  },

  unknown: {
    label: "Unknown",
    icon: "?",
    description:
      "La combinación actual de servicios no corresponde a un modo conocido.",
  },
};

const STATE_LABELS = {
  running: "En ejecución",
  starting: "Iniciando",
  stopped: "Detenido",
  error: "Error",
};

const elements = {
  modeBadge: document.querySelector("#mode-badge"),
  modeIcon: document.querySelector("#mode-icon"),
  modeTitle: document.querySelector("#mode-title"),
  modeDescription: document.querySelector("#mode-description"),

  codeServerStatus: document.querySelector("#code-server-status"),
  ollamaStatus: document.querySelector("#ollama-status"),
  jupyterStatus: document.querySelector("#jupyter-status"),

  copilotButton: document.querySelector("#copilot-button"),
  trainButton: document.querySelector("#train-button"),
  stopButton: document.querySelector("#stop-button"),
  refreshButton: document.querySelector("#refresh-button"),

  transitionMessage: document.querySelector("#transition-message"),
  errorMessage: document.querySelector("#error-message"),

  jupyterLink: document.querySelector("#jupyter-link"),
};

let currentMode = "unknown";
let operationInProgress = false;

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ??
        `La API ha respondido con el código ${response.status}.`,
    );
  }

  return data;
}

function updateServiceStatus(element, state) {
  const normalizedState = state ?? "error";

  element.className =
    `service-status status-${normalizedState}`;

  element.innerHTML = `
    <span class="status-dot"></span>
    ${STATE_LABELS[normalizedState] ?? normalizedState}
  `;
}

function updateInterface(status) {
  currentMode = status.mode ?? "unknown";

  const mode = MODE_DATA[currentMode] ?? MODE_DATA.unknown;

  elements.modeBadge.textContent = mode.label;
  elements.modeBadge.className =
    `mode-badge mode-${currentMode}`;

  elements.modeIcon.textContent = mode.icon;
  elements.modeTitle.textContent = mode.label;
  elements.modeDescription.textContent = mode.description;

  updateServiceStatus(
    elements.codeServerStatus,
    status.services?.code_server,
  );

  updateServiceStatus(
    elements.ollamaStatus,
    status.services?.ollama,
  );

  updateServiceStatus(
    elements.jupyterStatus,
    status.services?.jupyter,
  );

  const jupyterIsRunning =
    status.services?.jupyter === "running";

  elements.jupyterLink.classList.toggle(
    "disabled",
    !jupyterIsRunning,
  );

  updateButtons();
}

function updateButtons() {
  const disabled = operationInProgress;

  elements.copilotButton.disabled =
    disabled || currentMode === "copilot";

  elements.trainButton.disabled =
    disabled || currentMode === "train";

  elements.stopButton.disabled =
    disabled || currentMode === "stopped";

  elements.refreshButton.disabled = disabled;
}

function showError(message) {
  elements.errorMessage.textContent = message;
  elements.errorMessage.classList.remove("hidden");
}

function hideError() {
  elements.errorMessage.classList.add("hidden");
  elements.errorMessage.textContent = "";
}

async function loadStatus() {
  try {
    const status = await apiRequest("/status");

    updateInterface(status);
    hideError();
  } catch (error) {
    showError(error.message);
  }
}

async function changeMode(mode) {
  operationInProgress = true;
  hideError();

  elements.transitionMessage.classList.remove("hidden");

  elements.copilotButton.textContent =
    mode === "copilot"
      ? "Activando Copilot..."
      : "Activar Copilot";

  elements.trainButton.textContent =
    mode === "train"
      ? "Activando Train..."
      : "Activar Train";

  elements.stopButton.textContent =
    mode === "stop"
      ? "Deteniendo..."
      : "Detener GPU";

  updateButtons();

  try {
    const response = await apiRequest(`/${mode}`, {
      method: "POST",
    });

    updateInterface(response.status);
  } catch (error) {
    showError(error.message);
    await loadStatus();
  } finally {
    operationInProgress = false;

    elements.transitionMessage.classList.add("hidden");

    elements.copilotButton.textContent = "Activar Copilot";
    elements.trainButton.textContent = "Activar Train";
    elements.stopButton.textContent = "Detener GPU";

    updateButtons();
  }
}

elements.copilotButton.addEventListener("click", () => {
  changeMode("copilot");
});

elements.trainButton.addEventListener("click", () => {
  changeMode("train");
});

elements.stopButton.addEventListener("click", () => {
  changeMode("stop");
});

elements.refreshButton.addEventListener("click", () => {
  loadStatus();
});

loadStatus();

window.setInterval(() => {
  if (!operationInProgress) {
    loadStatus();
  }
}, 5000);
