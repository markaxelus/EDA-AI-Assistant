# EDA-AI-Assistant

An AI-driven automation tool that analyzes Electronic Design Automation (EDA) tool logs to identify, cluster, and provide intelligent explanations for design errors and warnings. This system bridges the gap between complex semiconductor design workflows and actionable engineering insights.

## What this is

The EDA-AI-Assistant is an intelligent log analysis pipeline that processes Icarus Verilog and Yosys synthesis tool outputs, automatically clusters similar errors/warnings, and generates human-readable explanations with suggested fixes using Google's Gemini AI. It transforms verbose, technical EDA logs into structured, actionable engineering reports that accelerate debugging and design iteration cycles.

## Why it matters

This project directly addresses the critical need for AI-driven automation in semiconductor design workflows, mirroring the industry's push toward intelligent tooling that reduces manual debugging time and accelerates time-to-market for complex chip designs. By automating the analysis of EDA tool outputs, a traditionally time-intensive manual process, this system enables engineering teams to focus on design innovation rather than log parsing, supporting the broader semiconductor industry's transition to AI-enhanced development environments.

## How to run

### Docker (Recommended)
```bash
# Setup environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run analysis
docker-compose --profile production up
```

### Local Python
```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate  # Linux/Mac
python -m venv .venv && .\.venv\Scripts\Activate.ps1  # Windows

# Install and run
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key_here" > .env
python -m src.ai_logs.main --iverilog-log data/verilog_small.log --yosys-log data/yosys_small.log
```

**Sample Output[MD]:** [View Generated Report](data/reports/report.md) - See the AI-generated analysis of EDA tool logs with intelligent explanations and suggested fixes.  
**Sample Output[JSON]:** [View Generated Report](data/processed/results.json)   

> Note that some clusters with `warning` and `info` labels will not have a summary or suggested_fixes unless they are recurring, which is intended by design.

> **Note on file/line locations:**    
> - The bundled sample logs (`src/data`) don’t include file names or line numbers, because the generated sample reports do not contain that information.    
> - In real production logs, most errors and warnings from tools like Icarus Verilog or Yosys include `file:line` references (e.g., `alu.v:105`).    
> - When present, these locations can be easily parsed and included in the cluster summaries, making the report seem less trivial and more actionable.  

## Feedback loop [Proof of Concept]

Continuous improvement can be built into the system through an integrated feedback mechanism. Users can provide feedback on AI-generated explanations and suggested fixes via the embedded feedback form in each generated report. This iterative feedback loop drives model refinement and ensures the tool evolves with real-world engineering challenges. The system is designed for extensibility, future versions will support additional EDA tools (Synopsys, Cadence), enhanced clustering algorithms, and integration with a more robust CI/CD pipelines for automated design validation.

## Tech

**Core Technologies:**

- **AI/ML**: Google Gemini 2.5 Flash for intelligent log analysis and explanation generation
- **Python**: Modern Python with Pydantic for data validation and Typer for CLI interface
- **EDA Tools**: Icarus Verilog and Yosys synthesis tool log parsing
- **Data Processing**: Advanced clustering algorithms with fingerprinting for log message normalization
- **Output**: Structured JSON and Markdown report generation

**Architecture:**

- Modular pipeline design (parse → cluster → summarize → report)
- Extensible tool support framework
- Robust error handling and fallback mechanisms
- Comprehensive test coverage with pytest

**Testing:**

```bash
# Run the test suite
python -m pytest src/tests/ -v

# Run specific test modules
python -m pytest src/tests/test_parse.py -v
python -m pytest src/tests/test_normalize.py -v
python -m pytest src/tests/test_summarize.py -v
python -m pytest src/tests/test_report.py -v
```

The test suite covers all core functionality including log parsing, clustering algorithms, AI integration, and report generation. Tests validate both individual components and end-to-end pipeline behavior.

**Semiconductor Design Integration:**

- Direct integration with industry-standard EDA toolchains
- Support for Verilog/SystemVerilog design flows
- Automated error pattern recognition and classification
- Engineering-friendly report formatting for design review processes



