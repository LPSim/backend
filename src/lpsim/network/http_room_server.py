import os
import platform
import uvicorn
import signal
import time
import logging
import random
import threading
from fastapi.responses import JSONResponse
from typing import List, Tuple
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from multiprocessing import Process, Queue

from .http_server import HTTPServer
from .. import __version_tuple__, __version__  # type: ignore


class OneRoomWorker(Process):
    def __init__(self, cmd_queue: Queue, resp_queue: Queue, post_queue: Queue):
        """
        Initializes the OneRoomWorker class.

        Args:
            cmd_queue (Queue): The queue used to send arguments and messages about
                running the server.
            resp_queue (Queue): The queue used to send responses.
            post_queue (Queue): The queue used to send timestamps when a POST request
                is received.
        """
        super().__init__()
        self.cmd_queue = cmd_queue
        self.resp_queue = resp_queue
        self.post_queue = post_queue

    def run(self):
        """
        Receives init_args, run_args and room_port_range from `self.cmd_queue`,
        creates an `HTTPServer` and runs it with the given args until a SIGINT is
        received, then sends a message to the queue and waits for the next args. If
        None is received, it exits.

        Raises:
            Exception: Describes any exceptions that might be thrown.
        """
        while True:
            try:
                init_args, run_args, room_port_range = self.cmd_queue.get()
                if init_args is None:
                    # when receive None, return
                    break
                self.server = HTTPServer(**init_args)
                self.port = None

                # self.server.app.add_middleware(
                #     PostTimestampMiddleware, post_queue = self.post_queue)

                @self.server.app.middleware("http")
                async def post_timestamp_sender(request: Request, call_next):
                    if request.method == "POST":
                        self.post_queue.put(time.time())
                    response = await call_next(request)
                    return response

                @self.server.app.on_event("startup")
                def startup_event():
                    self.resp_queue.put(str(self.port))

                max_retry = 100
                for _ in range(max_retry):
                    try:
                        # try to occupy random port from room_port_range
                        self.port = random.randint(*room_port_range)
                        self.server.run(**run_args, port=self.port)
                        self.server.save_log(self.server.reset_log_save_file)
                        # when receive sigint, gracefully end server and send
                        # message to queue
                        self.resp_queue.put(
                            {
                                "decks": self.server.uploaded_deck_codes,
                            }
                        )
                        break
                    except SystemExit:
                        # start failed, send message to queue
                        self.resp_queue.put("invalid and retry")
                else:
                    self.resp_queue.put("server failed to start")
            except KeyboardInterrupt:
                # when receive sigint when waiting for args, simply ignore it
                pass


class HTTPRoomServer:
    """
    HTTP room server that host multiple rooms, each room is a HTTP server.
    Room will occupy a port, room server will deal with requests from client,
    to reset/start a new room etc, and tell client the room name and
    link of the server.
    It only starts rooms with same rules now. When running on Linux, it will
    collect deck codes of stopped rooms, but not on Windows.

    Args:
        max_rooms (int): Max number of rooms that can be created. All rooms
            will be created at the beginning.
        room_port_range (List[int]): Range of ports that can be used to
            create rooms. ports will be chosen in random order.  If no port is
            available but the room number is not reached, the room server will
            raise error and exit.
        room_timeout (int): Timeout of a room in seconds. If any valid action
            is performed, the timeout will be reset. Room server will
            periodically check the timeout and close the room if timeout.
        admin_password (str): Password for admin. Admin can reset or remove
            any room. If configured, only admin can see all room ids, and
            decks used for different rooms.
        allow_origins (List[str]): List of origins that are allowed to connect.
        reset_log_save_path (str): Path to save reset log.
        init_args (dict): Args for HTTPServer.__init__, e.g. match_config.
        run_args (dict): Args for HTTPServer.run, e.g. HTTPS certificate. But
            not port, which will be chosen randomly from room_port_range.
    """

    def __init__(
        self,
        max_rooms: int = 2,
        port: int = 7999,
        room_port_range: List[int] = [8000, 9000],
        room_timeout: int = 3600,
        admin_password: str = "",
        allow_origins: List[str] = ["*"],
        init_args: dict = {},
        run_args: dict = {},
    ):
        self.max_rooms = max_rooms
        self.port = port
        self.room_port_range = room_port_range
        self.room_timeout = room_timeout
        self.admin_password = admin_password
        self.allow_origins = allow_origins
        self.init_args = init_args
        self.run_args = run_args

        self.deck_history: List[Tuple[str, str]] = []

        self._check_time_interval = 5

        if platform.system() == "Windows":
            logging.warning(
                "Windows system detected, room server will use terminate "
                "instead of graceful shutdown, and cannot collect uploaded "
                "deck information."
            )

        self.app = FastAPI()
        app = self.app

        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            # allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_middleware(GZipMiddleware)

        @app.get("/version")
        async def get_version():
            """
            Return the version of lpsim.
            """
            return {
                "version": __version__,
                "version_tuple": __version_tuple__,
                "info": {
                    "class": "HTTPRoomServer",
                },
            }

        @app.post("/room/{room_name}")
        def post_room_name(room_name: str):
            """
            Create a new room with given name. If room is already created,
            return its port.

            Args:
                room_name (str): The name of the room.

            Returns:
                JSONResponse: The response containing the port (if success) and status
                of the room. When status is exist or created, the corresponding port
                will be returned. Otherwise, only status will be returned.
            """
            if room_name in self.room_names:
                idx = self.room_names.index(room_name)
                return JSONResponse({"port": self.room_ports[idx], "status": "exist"})
            else:
                if None not in self.room_names:
                    return JSONResponse({"status": "full"})
                # create new one
                idx = self.room_names.index(None)
                init_args = self.init_args.copy()
                init_args["room_name"] = room_name
                cmd_q, resp_q, post_q = self.queues[idx]
                cmd_q.put((init_args, self.run_args, self.room_port_range))
                while True:
                    resp = resp_q.get()
                    if resp == "server failed to start":
                        return JSONResponse({"status": "failed"})
                    else:
                        # is port, but may start failed, need to check
                        # whether fail message is sent
                        if resp_q.empty():
                            # if is empty, wait a minute and check again
                            time.sleep(0.1)
                        if resp_q.empty():
                            # queue empty, start success
                            self.room_names[idx] = room_name
                            self.room_ports[idx] = int(resp)
                            self.room_active_times[idx] = time.time()
                            return JSONResponse(
                                {"port": self.room_ports[idx], "status": "created"}
                            )
                        else:
                            # start failed with message
                            resp = resp_q.get()
                            assert resp == "invalid and retry"

        @app.delete("/room/{room_name}")
        def delete_room_name(room_name: str, password: str = ""):
            """
            Delete a room with given name. If room is not created, return
            error.

            Args:
                room_name (str): The name of the room.
                password (str): The password for the admin.

            Returns:
                JSONResponse: The response containing the action status (not exist or
                deleted).
            """
            if password != self.admin_password:
                return JSONResponse(status_code=403, content="wrong password")
            if room_name not in self.room_names:
                return JSONResponse({"status": "not exist"}, 404)
            else:
                idx = self.room_names.index(room_name)
                self._delete_one_room(idx)
                return JSONResponse({"status": "deleted"})

        @app.get("/rooms")
        def get_rooms(password: str = ""):
            """
            Get all rooms' name and port.

            Args:
                password (str): The password for the admin.

            Returns:
                JSONResponse: The response containing the rooms' name, port and timeout.
            """
            if password != self.admin_password:
                return JSONResponse(status_code=403, content="wrong password")
            return JSONResponse(
                {
                    "rooms": [
                        {
                            "name": name,
                            "port": port,
                            "timeout": int(self.room_timeout - time.time() + at),
                        }
                        for name, port, at in zip(
                            self.room_names, self.room_ports, self.room_active_times
                        )
                        if name is not None
                    ]
                }
            )

        @app.get("/decks")
        def get_decks(password: str = ""):
            """
            Get all decks used in rooms.

            Args:
                - password (str): The password for the admin.

            Returns:
                - JSONResponse: The response containing the decks used in rooms.
            """
            if password != self.admin_password:
                return JSONResponse(status_code=403, content="wrong password")
            return JSONResponse(self.deck_history)

    def _create_room_workers(self):
        max_rooms = self.max_rooms
        self.workers = []
        self.queues: List[Tuple[Queue, Queue, Queue]] = []
        # when name is None, room has no name and is ended
        self.room_names: List[str | None] = [None] * max_rooms
        self.room_ports: List[int] = [0] * max_rooms
        self.room_active_times: List[float] = [1e100] * max_rooms
        for _ in range(max_rooms):
            cmd_queue = Queue()
            resp_queue = Queue()
            post_queue = Queue()
            worker = OneRoomWorker(cmd_queue, resp_queue, post_queue)
            worker.start()
            self.workers.append(worker)
            self.queues.append((cmd_queue, resp_queue, post_queue))

    def run(self, *argv, **kwargs):
        """
        Create room workers, start them and run room server.
        When HTTPRoomServer stopped, stop all workers and stop check interval.
        All args will be passed to uvicorn.run, except port, which is not allowed.
        """
        if len(argv):
            raise ValueError("positional arguments not supported")

        # create room workers
        self._create_room_workers()

        # start check interval
        self._stop_interval = False
        self._stop_interval_success = False
        self._check_interval_func()

        # start room server
        assert "port" not in kwargs
        kwargs = kwargs.copy()
        kwargs["port"] = self.port
        uvicorn.run(self.app, **kwargs)

        # after run, mark _stop_interval as True, and wait for stop success
        logging.warning(
            "stopping interval check, it should take at most "
            f"{self._check_time_interval} seconds."
        )
        self._stop_interval = True
        while not self._stop_interval_success:
            time.sleep(0.1)
        self._stop_interval = False
        self._stop_interval_success = False

        # after run, stop all worker rooms
        for idx, (worker, queue, name) in enumerate(
            zip(self.workers, self.queues, self.room_names)
        ):
            if name is not None:
                self._delete_one_room(idx)

        if platform.system() != "Windows":
            # for OS other than windows, send stop signal to all workers and
            # join
            for worker, queue in zip(self.workers, self.queues):
                queue[0].put((None, None, None))
                worker.join()

    def _delete_one_room(self, room_idx: int):
        if platform.system() == "Windows":
            self._delete_one_room_by_terminate(room_idx)
        else:
            self._delete_one_room_gracefully(room_idx)

    def _delete_one_room_gracefully(self, room_idx: int):
        room_name = self.room_names[room_idx]
        assert room_name is not None
        worker = self.workers[room_idx]
        pid = worker.pid
        os.kill(pid, signal.SIGINT)
        msg = self.queues[room_idx][1].get()
        decks = msg["decks"]
        for deck in decks:
            self.deck_history.append((room_name, deck))
        room_port = self.room_ports[room_idx]
        logging.warning(f"room {room_name}:{room_idx}:{room_port} stopped")
        self.room_names[room_idx] = None
        self.room_ports[room_idx] = 0

    def _delete_one_room_by_terminate(self, room_idx: int):
        room_name = self.room_names[room_idx]
        assert room_name is not None
        worker = self.workers[room_idx]
        pid = worker.pid
        os.kill(pid, signal.SIGTERM)
        room_port = self.room_ports[room_idx]
        logging.warning(f"room {room_name}:{room_idx}:{room_port} terminated")
        # as it terminates, we cannot receive deck histories, and we need to
        # re-create a new worker.
        new_worker = OneRoomWorker(*self.queues[room_idx])
        new_worker.start()
        self.workers[room_idx] = new_worker
        self.room_names[room_idx] = None
        self.room_ports[room_idx] = 0

    def _remove_unused_rooms(self):
        """
        Check if any room is not used for a long time, and remove it if so.
        """
        for room_idx, room_name in enumerate(self.room_names):
            if room_name is None:
                continue
            post_queue = self.queues[room_idx][2]
            while not post_queue.empty():
                self.room_active_times[room_idx] = post_queue.get()
            if time.time() - self.room_active_times[room_idx] > self.room_timeout:
                logging.warning(f"room {room_name}:{room_idx} timeout")
                self._delete_one_room(room_idx)

    def _check_interval_func(self):
        self._remove_unused_rooms()
        if self._stop_interval:
            self._stop_interval_success = True
            return
        threading.Timer(self._check_time_interval, self._check_interval_func).start()


__all__ = ["HTTPRoomServer"]
