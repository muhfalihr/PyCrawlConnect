# INSTALLATION & SETUP PYTHON

![](https://github.com/muhfalihr/mystorage/blob/master/8151440.jpg?raw=true)

- Open a VM that is specifically for Kafka (Because the Python installation is required by Kafka).

- Install Python version 3.

  ```sh
  apt install python3
  ```

- Instal Virtual environment for Python version 3.

  ```sh
  apt install python3-venv
  ```

- Create a Python virtual environment using the venv module.

  ```sh
  python3 -m venv .venv/my-venv
  ```

- Install the python package according to the requirements.txt file.
  ```sh
  .venv/my-venv/bin/pip install -r requirements.txt
  ```
