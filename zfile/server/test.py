while True:
    inp = input(">>> ")
    for char in inp:
        if ' ' in char:
            inp = inp.replace(' ', '$')
    print(inp)
