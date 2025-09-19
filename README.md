# EDA-AI-Assistant

An AI-driven automation tool that analyzes Electronic Design Automation (EDA) tool logs to identify, cluster, and provide intelligent explanations for design errors and warnings. This system bridges the gap between complex semiconductor design workflows and actionable engineering insights.

## What this is

The EDA-AI-Assistant is an intelligent log analysis pipeline that processes Icarus Verilog and Yosys synthesis tool outputs, automatically clusters similar errors/warnings, and generates human-readable explanations with suggested fixes using Google's Gemini AI. It transforms verbose, technical EDA logs into structured, actionable engineering reports that accelerate debugging and design iteration cycles.

## Why it matters

This project directly addresses the critical need for AI-driven automation in semiconductor design workflows, mirroring the industry's push toward intelligent tooling that reduces manual debugging time and accelerates time-to-market for complex chip designs. By automating the analysis of EDA tool outputs—a traditionally time-intensive manual process—this system enables engineering teams to focus on design innovation rather than log parsing, supporting the broader semiconductor industry's transition to AI-enhanced development environments.

## How to run

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (add your Gemini API key)
echo "GEMINI_API_KEY=your_key_here" > .env

# Run the analysis pipeline with sample data
python -m src.ai_logs.main --iverilog-log data/verilog_small.log --yosys-log data/yosys_small.log
```

**Sample Output:** [View Generated Report](src/data/reports/report.md) - See the AI-generated analysis of EDA tool logs with intelligent explanations and suggested fixes.
Note that some clusters with `warning` and `info` labels will not have a summary or explanation which is intended by design. 

## Feedback loop

Continuous improvement is built into the system through an integrated feedback mechanism. Users can provide feedback on AI-generated explanations and suggested fixes via the embedded feedback form in each generated report. This iterative feedback loop drives model refinement and ensures the tool evolves with real-world engineering challenges. The system is designed for extensibility—future versions will support additional EDA tools (Synopsys, Cadence), enhanced clustering algorithms, and integration with CI/CD pipelines for automated design validation.

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

**Semiconductor Design Integration:**

- Direct integration with industry-standard EDA toolchains
- Support for Verilog/SystemVerilog design flows
- Automated error pattern recognition and classification
- Engineering-friendly report formatting for design review processes
