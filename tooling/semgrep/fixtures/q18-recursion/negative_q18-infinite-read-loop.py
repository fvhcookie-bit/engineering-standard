attempts = 0
while True:
    attempts += 1
    if attempts > 10:
        raise RuntimeError
    data = stream.read(1024)
