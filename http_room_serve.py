"""
Serve a room server on localhost:7999. Note you should wrap the server with
`if __name__ == '__main__':` to avoid error.
"""


from lpsim.network.http_room_server import HTTPRoomServer


if __name__ == "__main__":
    room_server = HTTPRoomServer(
        max_rooms=3,
        port=7999,
        room_port_range=[8001, 8010],
        room_timeout=300,
        admin_password="foobar",
        run_args={},
    )
    room_server.run()
    print("server closed")
