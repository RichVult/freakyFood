Quickstart Guide
================

This is a quickstart guide for using FreakyFood.

- Step 1: Clone the repository.
To clone the repository, run the following command:

.. code-block:: bash


    git clone https://github.com/RichVult/freakyFood.git

- Step 2: Install Python 3.12.7 and virtualenv.
Ensure that Python 3.12.7 is installed on your system. You can check the installed version by running:

.. code:: bash


    python --version

If you don't have `virtualenv` installed, you can install it via pip:

.. code:: bash


    pip install virtualenv

- Step 3: Create and activate a virtual environment.
Navigate to the project directory and create a virtual environment:

.. code:: bash


    cd /path/to/your/project
    python -m venv .venv

After the virtual environment is created, activate it:

- On Windows:
- 
.. code:: bash


    venv\Scripts\activate

- On macOS/Linux:

.. code:: bash


    source venv/bin/activate

- Step 4: Install the dependencies.
With the virtual environment activated, install the required dependencies by running:

.. code:: bash


    pip install -r project/requirements.txt
    
- Step 5: Run the application.
To run the application, use the following command:

.. code:: bash


    python project/app.py

This will start the FreakyFood application. Follow any additional setup instructions in the documentation if needed.