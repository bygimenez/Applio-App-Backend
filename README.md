![APP Screenshot](https://i.imgur.com/RSFLuaL.png)
<p align="center">
  The easiest voice cloning tool, now in app. Made to be simple, fast and light.
</p>

# Backend

This is the backend of the Applio APP, powered by Flask and [RVC-CLI](https://github.com/blaise-wf/rvc-cli) from **blaisewf** for voice processing. If you're interested in contributing to the project or exploring its functionality, follow the instructions below.

## Prerequisites

Ensure you have the following installed:

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

## Development Setup

Follow these steps to set up your development environment:

### 1. Clone the repository
```bash
git clone https://github.com/bygimenez/applio-app-backend.git python
```

### 2. Create a virtual environment
```bash
python -m venv env
```

### 3. Activate the virtual environment

- On macOS/Linux:
  ```bash
  source env/bin/activate
  ```
- On Windows:
  ```bash
  .\env\Scripts\activate
  ```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the server
```bash
python server.py
```

## Running the Frontend

For frontend development, refer to the [Applio APP Frontend](https://github.com/bygimenez/applio-app) repository.

## Contributing

We welcome contributions! Please follow the standard GitHub flow: fork the repository, make your changes, and open a pull request. 

---

For any questions or issues, feel free to open an issue in the repository or reach out to the project maintainers.
