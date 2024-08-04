from argparse import ArgumentParser
import sys

arg_parser = ArgumentParser(description="GitWhisper: A chatbot to help you with Git repositories")
arg_group = arg_parser.add_mutually_exclusive_group()
arg_group.add_argument("--ui", action="store_true", default=True, help="Use GitWhiper in a UI")
arg_group.add_argument("--cli", action="store_true", default=False, help="Use GitWhiper in the terminal")
args = arg_parser.parse_args()

if args.cli:
    import gitwhisper_ai

    gitwhisper_ai.open_repository(input("Repository path: "))
    gitwhisper_ai.start_chat()

    placeholder = "User (type 'exit' to exit): "

    while True:
        usr_inp = input(placeholder)

        if usr_inp.lower() == "exit":
            sys.exit(0)

        print("GitWhisper: ", end='', flush=True)

        resp = gitwhisper_ai.send_message(usr_inp, stream=True)

        for chunk in resp:
            print(chunk.text, flush=True, end='')

        placeholder = "User: "