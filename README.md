[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/SCA-edx6)

<div align="center">

# OcrRoo

## v1 - Drafted by Rafael Avigad/James Makela

---

[Badges here]

**AI Powered OCR Code Recognition from Video Tutorials**

[![Build](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/actions/workflows/build.yml/badge.svg)](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/actions/workflows/build.yml)
[![Tests](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/actions/workflows/tests.yml/badge.svg)](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/actions/workflows/tests.yml)
[![Accessibility](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/actions/workflows/accesibility.yml/badge.svg)](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/actions/workflows/accesibility.yml)

</div>

## About

A video player designed to assist visually impaired developers who want to learn to code.
The program reads code from videos to assist visually impaired developers in using these resources.

## Features - (need more info) TODO

---

[Demo Video here]

- Ability to upload, or enter a video link.
- OcrRoo picks out any code text from the provided video, and reads that text to the user.

## Installation

To install and run this project, please follow the [Installation Guide](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/wiki/Installation-Guide)
in the [Wiki](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/wiki).

#### Basic Installation

1. Navigate to the projects root folder

2. Create a virtual environment

   ```bash
   python -m venv ./venv
   ```

3. Activate the virtual environment
   Windows:

   ```bash
   ./venv/Scripts/activate
   ```

   Mac/Linux

   ```bash
   source venv/bin/activate
   ```

4. Install dependencies with pip

   ```bash
   pip install -r requirements.txt
   ```

5. This project requires the Tesseract OCR Library (note: may require an installer).

   Tesseract OCR Documentation: https://tesseract-ocr.github.io/tessdoc/Installation.html
   
   Windows Installer: https://github.com/UB-Mannheim/tesseract/wiki
   
   WARNING: Tesseract should be either installed in the directory which is suggested during the installation or in a 
   new directory. The uninstaller removes the whole installation directory. If you installed Tesseract in an existing 
   directory, that directory will be removed with all its subdirectories and files.

   Refer to: [AppSettings] in app/config.ini

## Configuration / Initial SetUp

1. The project requires a personal ChatGPT API Key. 

   OpenAI API: https://openai.com/index/openai-api/ 
   Refer to:[AppSettings] in app/config.ini

2. The project requires the path to your IDE executable: 
   Refer to: [AppSettings] in app/config.ini


## Running the Project

1. Once the Installation and Configuration/SetUp steps have been completed; navigate and run:
   ```bash
   app/app.py
   ```

2. Once running, the terminal will display the localhost link for the project in the console.

## Contributing

To contribute to this project, please follow the [Contribution Guide](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/wiki/Contribution-Guide)
in the [Wiki](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/wiki).

## Code of Conduct

---

- To view the code of conduct, please visit the [Code of Conduct] page in the [Wiki](https://github.com/NM-TAFE/project-advanced-ui-development-team-mental-capacity/wiki).

## License

This project is licensed under the [Creative Commons Zero v1.0 Universal](LICENSE) license.

## Credits

This code was first created by the 2023, S2 Advanced Programming Diploma Group at North Metro TAFE. If you would like your contribution acknowledged, please contact Rafael.
