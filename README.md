# 🎯 Exec Meeting Prep Agent

**An AI-powered Rhythm of Business (ROB) automation tool that tracks executive meeting readiness, generates Summary by Speaker documents, and works seamlessly with Microsoft Copilot.**

[![GitHub Actions](https://github.com/jay9parmar/exec-meeting-prep-agent/actions/workflows/meeting-readiness-check.yml/badge.svg)](https://github.com/jay9parmar/exec-meeting-prep-agent/actions/workflows/meeting-readiness-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 What This Agent Does

This agent automates the **exact tasks** executive program managers do daily:

| Task | How Agent Handles It |
|------|---------------------|
| Track meeting readiness | One command shows agenda, slides, BM confirmation status |
| Chase BMs for content | Auto-generates missing items list |
| Create SbS documents | `--generate-sbs` creates formatted summaries instantly |
| Cross-org coordination | Single tracker holds meetings from MCAPs, CE&S, GCS |
| Daily status checks | GitHub Actions runs automatically at 9 AM |
| Executive inquiries | Copilot reads tracker and answers natural language questions |

---

## 🚀 Quick Demo (30 Seconds)

```bash
# Clone the repository
git clone https://github.com/jay9parmar/exec-meeting-prep-agent.git
cd exec-meeting-prep-agent

# Run the readiness check
python src/main.py --check-readiness
