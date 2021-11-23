# Project Title
Visualization of COVID-19 data in the Netherlands.

## Description
This respository is built to analyze/visualize COVID-19 related data. The dashboard is hosted [HERE](http://shriniwas26.ddns.net/covid-nl/).

## Getting Started

### Dependencies

* Should work on any OS, but I've only tested on MacOS(11.6) and Ubuntu (20.04).
* Python 3.8
* Anaconda (pip might work as well)

### Installing

* Clone the repo

* Create a conda environment & activate it
    ```{bash}
    conda create --name dashboards-env python=3.8
    conda activate dashboards-env
    ```

* Install requirements
    ```
    conda install --file requirements.txt
    ```

### Executing program

* Change to the project directory.
* Run in deployment
    ```{bash}
    gunicorn --bind 127.0.0.1:5005 covid-dashboard-nl:server
    ```
* Run for development (for auto-reloading on source change)
    ```{bash}
    python3 covid-dashboard-nl.py
    ```
* Update to the latest data, as published by RIVM
    ```{bash}
    python3 update_data.py
    ```

## Todos
- [ ] Add deployment instructions.

## Help
* If you find any issues please open an issue on GitHub.
* Of course, any suggestions and/or feedback is always welcome. Please contact me [here](shriniwas92@gmail.com)

<!-- ## Authors -->

<!-- ## Version History
-->

<!-- ## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46) -->
