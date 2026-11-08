<div align="center">

## Thanh Son Potherat

**Data & AI engineering student @ ESILV Paris** · looking for a **6-month Data Engineering / ML Engineering internship from April 2027**

<a href="https://www.linkedin.com/in/thanh-son-potherat-b793b333a/">
  <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
</a>

</div>

### About Me & My Engineering Journey

I am an engineering student specializing in **Data and Artificial Intelligence** at **ESILV** in Paris. My core focus lies in transforming raw data into robust pipelines and bridging the gap between local model development and production environments.

**Education:** ESILV (Data & AI Major). Previously attended Hanyang University (Seoul) and completed a Physics & Chemistry Preparatory Class.<br>
**Availability:** Currently seeking a 6-month internship in **Data Engineering or Machine Learning Engineering** starting **April 2027**.<br>
**Languages:** French (Native), English.

<a href="https://thanh-poth.github.io/Thanh-Poth/"><img src="https://raw.githubusercontent.com/Thanh-Poth/Thanh-Poth/output/aquarium.svg" width="100%" alt="Animated ASCII ocean: each animal is one of my repositories. Click to open the interactive version." /></a>

---

### Technical Skills

<div align="center">

  **Data Engineering & Processing**<br>
  [![Data Skills](https://skillicons.dev/icons?i=postgres,py,cpp,bash&theme=dark)](https://skillicons.dev)<br>
  <img src="https://img.shields.io/badge/Polars-0033A0?style=flat-square&logo=polars&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white" />

  <br><br>
  **MLOps, Backend & Deployment**<br>
  [![MLOps Skills](https://skillicons.dev/icons?i=docker,fastapi,git,github,linux&theme=dark)](https://skillicons.dev)<br>
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=mlflow&logoColor=white" />
  <img src="https://img.shields.io/badge/ONNX-005CED?style=flat-square&logo=onnx&logoColor=white" />

  <br><br>
  **Machine Learning Modeling**<br>
  [![ML Skills](https://skillicons.dev/icons?i=sklearn,pytorch,tensorflow&theme=dark)](https://skillicons.dev)<br>
  <img src="https://img.shields.io/badge/LightGBM-008000?style=flat-square&logo=l&logoColor=white" />

</div>

---

### Featured Projects

#### 🍄 [Mushroom Finder](https://github.com/Thanh-Poth/Mushroom_Finder): open-data geospatial pipeline

> An interactive map that scores every public forest area in mainland France (0–100) for six edible mushroom species, by joining three open data sources: ONF public forests, IGN BD Forêt® V2 tree stands and Open-Meteo weather (14 days of history + 3-day forecast).

- **Ingestion**: WFS requests split into fixed 0.2° tiles, pages of 5,000 features, at most 8 concurrent requests, weather batched by 50 points.
- **Processing**: Shapely intersection of forests × tree stands, then a scoring model fully driven by YAML config (32 tree-stand codes mapped to categories).
- **Storage & resilience**: SQLite cache (compressed WKB/JSON, 30-day and 3-hour TTL) with stale-data fallback; when an upstream service is down, the API still answers or returns a clear 503.
- **Quality**: pytest suite (scoring, resilience to outages, security), Docker Compose for the FastAPI backend and React + MapLibre frontend.

`Python` `FastAPI` `Shapely` `SQLite` `httpx` `React` `Docker`

#### 📈 [Tick-Level Data Processing](https://github.com/Thanh-Poth/Tick-Level_Financial_Data_Processing): high-frequency data pipeline

> Rebuilds six bar types (time, tick, volume, dollar, dollar-imbalance, run) from raw trades and measures which one gives the best-behaved returns.

- **Pipeline**: acquisition (generic source and MetaTrader 5) → event-driven resampling of 261k trades → statistical tests → CSV and plots, all from one `run_analysis.py` command.
- **Result**: dollar bars came closest to Gaussian (Jarque-Bera 1.5 vs 447.3 for time bars), with limitations documented honestly (simulated data).

`Python` `pandas` `NumPy` `statsmodels` `MetaTrader 5`

#### 🤖 [Local RAG Assistant](https://github.com/Thanh-Poth/RAG): ingestion to API, tested and containerised

> Retrieval-Augmented Generation API that answers only from the documents it is given and refuses below a 0.65 similarity threshold, instead of hallucinating.

- **Data flow**: document ingestion → sentence-transformers embeddings → persistent ChromaDB index → FastAPI `POST /ask`.
- **Engineering**: fully local on CPU (no paid API), pytest with mocked and integration tests, GitHub Actions CI, Docker image.

`Python` `FastAPI` `ChromaDB` `sentence-transformers` `Docker` `GitHub Actions`

<details>
<summary><b>More projects</b></summary>

- **[Quant Trading Dashboard](https://github.com/Thanh-Poth/Dashboard)**: full-stack app (FastAPI, React) running a quant research workflow, from market data collection to ML model optimization and backtesting.
- **[Strategy Backtesting Pipeline](https://github.com/Thanh-Poth/Strategy_Backtesting_Pipeline)**: modular Python architecture for risk-managed multi-asset portfolios, with causal walk-forward backtesting, risk-parity allocation and VaR budgeting.
- **[Sample Weights & Fractional Differentiation](https://github.com/Thanh-Poth/Sample-Weights-Fractional-Differentiation)**: fractional differentiation and sample weighting, tracked with MLflow.

</details>

---

### Beyond Engineering

When I am not configuring containers or optimizing pipelines, I maintain an active lifestyle through physical and creative disciplines:

*   **Badminton:** Competitive player in D5 interclub (FFBaD P10 ranking).
*   **Alpinism & Climbing:** Bouldering and lead climbing.

---

### GitHub Analytics

<div align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=Thanh-Poth&show_icons=true&theme=radical&hide_border=true" width="48%" alt="GitHub Stats" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=Thanh-Poth&layout=donut&theme=radical&hide_border=true" width="48%" alt="Top Languages" />
</div>

<details>
<summary><b>How to read the ocean</b></summary>

| Languages of the repo | Animal |
|---|---|
| Python + JavaScript/TypeScript (full-stack) or Python + Docker | hammerhead shark |
| Python | manta ray |
| TypeScript / JavaScript / C / C++ / Rust / Go / Java | shark |
| Jupyter Notebook and anything else | sea turtle |

The longer the animal, the more code in the repo. Click the ocean to open the [interactive version](https://thanh-poth.github.io/Thanh-Poth/): hover an animal to see its project, click it to open the repository.

</details>
