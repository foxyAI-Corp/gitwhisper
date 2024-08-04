import gitwhisper_ai
from argparse import ArgumentParser

arg_parser = ArgumentParser(description="GitWhisper: A chatbot to help you with Git repositories")
arg_group = arg_parser.add_mutually_exclusive_group()
arg_group.add_argument("--ui", action="store_true", default=True, help="Use GitWhiper in a UI")
arg_group.add_argument("--cli", action="store_true", default=False, help="Use GitWhiper in the terminal")
args = arg_parser.parse_args()

if args.cli:
    gitwhisper_ai.open_repository(input("Repository path: "))
    gitwhisper_ai.start_chat()

    while True:
        usr_inp = input("User: ")
        print("GitWhisper: ", end='')

        resp = gitwhisper_ai.send_message(usr_inp, stream=True)

        for chunk in resp:
            print(chunk.text, end='')