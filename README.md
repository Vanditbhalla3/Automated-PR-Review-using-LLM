# Automated-PR-Review-using-LLM
Pull Requests (PRs) are vital for code review but often time-consuming. This project leverages large language models (LLMs) to automate initial PR reviews, providing quick insights into code quality, best practices, and potential issues. The system aims to streamline the review process and improve code standards.

## Table of Contents
- Introduction
- Demo
- Overview
- Motivation
- Installation
- Technologies Used
- License
- Credits
- Project Status

## Introduction

In the realm of software development, PR reviews are essential for maintaining code quality and 
ensuring that new contributions align with project standards and objectives. However, the 
manual review process can be a bottleneck, leading to delays and potential inconsistencies in 
feedback. The proposed system seeks to automate the initial review process using LLMs, 
capable of understanding code context, identifying anti-patterns, and suggesting improvements. 
This approach not only accelerates the review process but also provides a consistent standard 
for code quality assessment.

## Demo 

Here are some screenshots of the reviews generated:

## Motivation

Pull Requests (PRs) are essential for code quality and collaboration in software development, but their review process can be time-consuming and subjective. To address these challenges, this project proposes an automated system utilizing large language models (LLMs) for initial PR reviews. By providing insights into code quality and adherence to best practices, this system aims to streamline the review process and improve code standards. This project, undertaken as part of my studies at **SRH Hochschule University**, in collaboration with **Auto1** to enhance their internal workflows.

## Installation

Follow these steps to install and setup the Code Reviewer:

1. **Clone the Repository**
   
   ```sh
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
2. **Create a Python Virtual Environment**
   
   ```sh
   python -m venv <your_venv_name>
3. **Activate the Virtual Environment**
   
   ```sh
   .\<your_venv_name>\Scripts\activate
4. **Install the Required Packages**

   ```sh
   pip install -r requirements.txt
5. **Set Up Environment Variables**
   
   Add your OpenAI GPT API Key and Github API Key
   ```sh
   OPENAI_API_KEY=your_openai_api_key_here
   GITHUB_API_KEY=your_github_api_key_here
6. **Run the PR Code Reviewer in Terminal**

   Add the link of the PR to be reviewed after the run command
   ```sh
   python PR_Code_Reviewer.py <PR_LINK>
   ```
## Technologies Used

- Python3
- OpenAI GPT-4o LLM 

## License
This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software under the terms of the MIT License.

See the [LICENSE](LICENSE) file for more details.

## Credits

## Project Status
This project is currently under active development. New features, improvements, and bug fixes are being added regularly. 