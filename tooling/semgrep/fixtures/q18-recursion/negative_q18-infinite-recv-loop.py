attempts = 0
while True:
    attempts += 1
    if attempts > 10:
        raise RuntimeError
    packet = sock.recv(4096)
