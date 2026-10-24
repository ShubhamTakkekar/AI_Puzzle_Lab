# AI PUZZLE LAB
### Interactive Intelligent Problem-Solving Simulator

**AI Puzzle Lab** is a professional educational application designed to teach classical artificial intelligence search algorithms and constraint satisfaction paradigms through visual simulations, mathematical constraint validation, live execution profiling, and empirical performance analysis.

---

## 🌟 Key Features & Architectural Modules

### 1. 🏠 Home Dashboard
- High-level overview of classical search paradigms: Uninformed Search, Informed (Heuristic) Search, and Constraint Satisfaction.
- Interactive launcher cards with direct navigation to all puzzle laboratories.
- Real-time active session telemetry counter tracking genuine search queries performed across the app.

### 2. 🧩 8-Puzzle Lab
- **State Representation:** 3x3 sliding tile board with 0 representing the blank tile.
- **Mathematical Solvability Pre-flight Check:** Analyzes inversion parity. Odd inversion counts are rejected before running costly searches, mathematically proving impossibility.
- **Algorithms Implemented:**
  - **A* Search:** Guided by the admissible and consistent Manhattan distance heuristic.
  - **Breadth-First Search (BFS):** Layer-by-layer exploration guaranteeing optimal (shortest) move sequence.
  - **Depth-First Search (DFS):** Bounded-depth exploration preventing runaway recursion.
- **Interactive Controls:** Direct board click-to-slide movement, custom state string input, presets (Trivial to Challenging), random solvable generator.
- **Solution Playback:** Full scrubber controls (`First`, `Prev`, `Play`, `Pause`, `Next`, `Last`, `Show Goal`, Speed Slider, Step Scrubber).
- **Dynamic Explanations:** Real-time physical move narration generated for each transition (e.g., "Empty slot moved Up, Tile 7 slid Down into Row 2, Col 3").
- **Telemetry:** Wall-clock execution time (ms), nodes explored, peak frontier size, and solution length.

### 3. 🌊 Missionaries & Cannibals Lab
- **Problem Modeling:** 3 missionaries and 3 cannibals crossing a river using a 2-person boat (supports configurable capacities).
- **Constraint Enforcement:** Missionaries may never be outnumbered by cannibals on either riverbank unless there are zero missionaries present.
- **Vector-Style River Scene:** High-contrast visual environment rendering the Left Bank, Boat with active passengers, and Right Bank.
- **Manual Crossing Mode:** Interactive passenger loading with real-time validation and illegal move warnings.
- **Algorithms:** Optimal BFS discovering the classic 11-step crossing sequence and bounded DFS.
- **Interactive Playback:** Automated play/pause, scrub slider, and dynamic step-by-step crossing narrative.

### 4. 🔢 Sudoku Lab (CSP)
- **Interactive 9x9 Grid:** Every cell is individually selectable with highlighted row, column, and matching numbers.
- **Real-Time Conflict Detection:** Duplicate values in any row, column, or 3x3 block are instantly highlighted in vivid warning red.
- **Palette Keypad:** On-screen number buttons (1–9) and Clear for seamless editing without keyboard constraints.
- **Dual Solving Modes:**
  - **Solve Instantly:** Immediate MRV backtracking solution display with execution metrics.
  - **Solve Step-by-Step:** Interactive playback of the backtracking solver's decision trace with decision logs (`TRY`, `BACKTRACK`, `SUCCESS`).
- **Validation & Solvability:** Detects contradictory initial inputs and puzzles with no mathematical solution without modifying original clues.

### 5. ⚔️ Algorithm Arena
- **Live Empirical Benchmarking:** Runs compatible algorithms simultaneously on identical puzzle configurations.
- **Direct Side-by-Side Comparison:** Compares execution time, explored states, peak memory, and path length.
- **Speedup & Node Reduction Ratios:** Quantifies algorithmic advantage (e.g. A* vs BFS efficiency).
- **Integrity Guarantee:** Zero hardcoded or fabricated statistics; all measurements are executed live on your local CPU.

### 6. 📈 Data Analytics & Telemetry
- **Statistical Aggregation:** Uses Pandas to aggregate session telemetry (Mean, Median, Min, Max, Count).
- **Midnight Graphite Matplotlib Charts:**
  - Mean Execution Time by Algorithm (ms)
  - Mean States Explored (Nodes)
  - Complexity Scatter: Runtime vs. Explored States
- **Data Export:** Single-click CSV export of raw experimental telemetry for academic analysis.

### 7. 🤖 Puzzle Difficulty Predictor
- **Machine Learning Integration:** Supervised `RandomForestClassifier` trained via Scikit-learn.
- **Ground Truth Methodology:** Optimal solution depths computed by A* search categorized into *Easy* (≤ 6 moves), *Medium* (7–12 moves), and *Hard* (≥ 13 moves).
- **Zero Target Leakage:** Features are strictly intrinsic geometric/permutation properties:
  - Manhattan distance
  - Misplaced tiles count
  - Inversion count
  - Linear conflicts count
  - Blank row and column coordinates
  - Tiles in correct rows/columns count
- **Evaluation & Diagnostics:** Reports test-set accuracy, precision, recall, F1-score, confusion matrix, and Gini feature importances.
- **Live Retraining:** Interface button to regenerate a fresh balanced dataset and retrain live.

---

## 📁 Project Architecture

```
AI_Puzzle_Lab/
├── algorithms/
│   ├── __init__.py
│   ├── astar.py              # A* heuristic search with priority queue
│   ├── bfs.py                # Breadth-First Search with node table
│   ├── dfs.py                # Bounded Depth-First Search with cycle detection
│   └── search_result.py      # Standardized SearchResult dataclass
├── puzzles/
│   ├── __init__.py
│   ├── eight_puzzle.py       # 8-Puzzle domain, validation & heuristics
│   ├── missionaries_cannibals.py # River crossing state & safety invariants
│   └── sudoku.py             # 9x9 CSP validation & MRV backtracking
├── analytics/
│   ├── __init__.py
│   ├── benchmark.py          # Synchronous multi-algorithm benchmarker
│   ├── data_analysis.py      # Pandas aggregation & CSV export
│   └── visualizations.py     # Dark-themed Matplotlib visual charts
├── machine_learning/
│   ├── __init__.py
│   ├── dataset_generator.py  # Reproducible dataset generator (A* labels)
│   ├── train_model.py        # Random Forest model training & persistence
│   ├── predict_difficulty.py # Inference pipeline & feature extractor
│   └── model_artifacts/      # Persisted joblib model and metrics.json
├── ui/
│   ├── __init__.py
│   ├── styles.py             # Deep navy/charcoal styling & CSS tokens
│   └── components.py         # Reusable cards, boards, and metric badges
├── views/
│   ├── __init__.py
│   ├── home.py               # Home dashboard
│   ├── eight_puzzle_view.py  # 8-puzzle visual interactive lab
│   ├── missionaries_view.py  # River crossing simulator
│   ├── sudoku_view.py        # Sudoku CSP lab
│   ├── arena_view.py         # Comparative benchmark arena
│   ├── analytics_view.py     # Analytics & charts
│   └── predictor_view.py     # ML difficulty predictor
├── tests/
│   ├── test_search.py        # BFS, DFS, A* correctness and limits
│   ├── test_eight_puzzle.py  # Solvability parity and heuristics
│   ├── test_missionaries_cannibals.py # River safety constraints
│   ├── test_sudoku.py        # Sudoku CSP & MRV backtracking
│   ├── test_analytics.py     # Benchmarking & CSV formatting
│   └── test_ml.py            # Feature extraction & ML model inference
├── app.py                    # Streamlit main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Installation & Running the Application

### 1. Activate the Virtual Environment

**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
.\.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 2. Launch the Application

From the project root directory with the virtual environment activated, execute:

```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the complete test suite using Pytest:

```bash
pytest -v
```

All 54 unit tests across search algorithms, domain rules, constraint validation, analytics, and machine learning execute cleanly in ~2 seconds.
