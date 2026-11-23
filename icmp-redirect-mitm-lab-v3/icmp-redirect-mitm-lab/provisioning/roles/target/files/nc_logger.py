#!/usr/bin/env python3
"""A minimal stand-in for `nc -lk -p <port>` that keeps accepting
connections and appends every received line to a log file with a
timestamp, so the Task-2 flag checker can inspect it later. Functionally
this behaves like netcat from the student's point of view: connect, type
lines, they show up on the "server" side."""
import socket
import sys
import datetime

PORT = int(sys.argv[1])
LOGFILE = sys.argv[2]

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", PORT))
srv.listen(5)

while True:
    conn, addr = srv.accept()
    with conn, open(LOGFILE, "a") as log:
        buf = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode(errors="replace").rstrip("\r")
                ts = datetime.datetime.utcnow().isoformat()
                log.write(f"{ts}\t{addr[0]}\t{text}\n")
                log.flush()
