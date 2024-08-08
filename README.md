<div align="center">

<h1>foxyAi GitWhisper</h1>
<img src="https://raw.githubusercontent.com/foxyAI-Corp/gitwhisper/main/logo.svg" width="150">

</div>

<br>
A chatbot to help you with Git repositories, such as editing, building, and running them.

## Description

This project is a chatbot that can assist you with various tasks related to Git repositories, such as:

- Help you for creating, cloning, and deleting repositories
- Help you for adding, committing, and pushing changes
- Help you for branching, merging, and resolving conflicts
- Help you for building and running code
- And more!

The chatbot uses Google's Gemini API to understand your queries and provide relevant responses. It can also give you tips and best practices for working with Git repositories.

## Screenshot

![Screenshot of GitWhisper UI version](https://raw.githubusercontent.com/foxyAI-Corp/gitwhisper/main/screenshot.png)

## Installation

To install the chatbot, you need to have Python 3.9 or higher and `pip` installed on your system. Then, follow these steps:

- Clone this repository to your local machine:
```sh
git clone https://github.com/foxyAI-Corp/gitwhisper.git
cd gitwhisper
```
- Install the required dependencies:
```sh
pip install -r requirements.txt
```
- Set the `GOOGLE_GENAI_APIKEY` environment variable to your Gemini API Key.

## Usage

You can run the chatbot in a UI (default) or in the terminal:
```sh
python chatbot.py [--ui | --cli]
```

To use the chatbot, you need to have a Git repository that you want to work with. The chatbot will ask you for the path to your repository and then start a conversation with you. You can ask the chatbot any question or request related to your repository, such as:

- **"How do I create a new branch?"**
- **"What is the status of my repository?"**
- **"How do I merge the master branch into my branch?"**
- **"How do I build and run my code?"**
- **"What is the last commit?"**

The chatbot will try to answer your question or perform your request, and give you feedback on the result. You can also ask the chatbot for help or exit the conversation at any time.

## License

This project is licensed under the GNU General Public License v2.0 - see the [`LICENSE`](https://github.com/foxyAI-Corp/gitwhisper/blob/main/LICENSE) file for details.
