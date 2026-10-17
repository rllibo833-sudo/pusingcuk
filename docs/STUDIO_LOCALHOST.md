# PusingCuk Studio via localhost

Studio serves the existing HTML and its APIs from one origin, so the browser does not need CORS exceptions or a token embedded in JavaScript.

## Start on a machine with Python 3.11+

From the repository root:

```sh
python -m pip install .
ollama pull qwen3:4b
pusingcuk-studio
```

Open `http://127.0.0.1:8765` on the same device. Ollama must be running locally at `http://127.0.0.1:11434`. Set `PUSINGCUK_AI_MODEL` to choose another installed Ollama model.

The browser uses:
- `GET /health` for bridge liveness
- `POST /api/run` to run the Python reference interpreter on the supplied `.cuk` source
- `POST /api/chat` to call the actual `PusingCukAssistant` implementation

## Android limitation

This is a localhost backend, not a standalone HTML-only runtime. A browser cannot launch Python or Ollama by itself. On Android, an installed host/runtime or an APK wrapper must start this service and the model before opening the local URL. GitHub Pages or opening `web/index.html` as a file cannot provide the backend.

## Safety

The service binds only to loopback and refuses a non-local bind. Program execution is **not** an OS sandbox; only run source code you trust. The default local AI model requires device resources and an installed Ollama runtime. The current service does not embed a model or bundle Ollama into an APK.
