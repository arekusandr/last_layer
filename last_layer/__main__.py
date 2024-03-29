import sys


from last_layer import scan_prompt


def entrypoint():
    if len(sys.argv) < 2:
        print("Usage: last_layer <prompt>")
        sys.exit(1)

    prompt = sys.argv[1]
    result = scan_prompt(prompt)
    print(result)
    sys.exit(0)


if __name__ == "__main__":
    entrypoint()
