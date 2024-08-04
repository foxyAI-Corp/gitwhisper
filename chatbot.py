import gitwhisper_ai

gitwhisper_ai.open_repository(input("Repository path: "))
gitwhisper_ai.start_chat()
while True:
    usr_inp = input("User: ")
    print("GitWhisper: ", end='')
    
    resp = gitwhisper_ai.send_message(usr_inp, stream=True)

    for chunk in resp:
        print(chunk.text, end='')