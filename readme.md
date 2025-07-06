# 🛠️ Project Setup Guide

This guide explains how to set up and run the project locally.

---

## 🚀 Requirements

- Python 3.11.9+ (Recommended: Use a virtual environment)
- pip or pipenv
-  SQLite (sqlite file is included)

---

## 📦 Installation

### 1. Install Python

Download and install Python from the official website: https://www.python.org/downloads/

### 2. Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Sqlite file is included in the project. No need to create a database or perform migrations.

---

## 🚀 Running the script

### 1.

```bash
cd scripts

## Run the following command to fetch emails from the gmail and save them in db
python3 fetch_and_process.py

# Run the following command to fetch the emails from db and perform the actions
#based on the rules defined in the config/rules.json
python3 process.py

```