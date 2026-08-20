import asyncio
import socket
import struct

smt_title_id = "0x40000000E5C00"


class AzaharException(Exception):
    pass


class ProcessInfo:

    def __init__(self, process_id: int, title_id: str):
        self.process_id = process_id
        self.title_id = title_id


class AzaharInterface:
    PACKET_VERSION: int = 1
    TYPE_NONE: int = 0
    TYPE_READ: int = 1
    TYPE_WRITE: int = 2
    TYPE_PROCESS_LIST: int = 3
    TYPE_SET_GET_PROCESS: int = 4
    HEADER_SIZE: int = 16
    MAX_READ_SIZE: int = 1024
    MAX_WRITE_SIZE: int = 24

    socket: socket.socket

    async def connect(self) -> bool:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(("127.0.0.1", 45987))
        self.socket.settimeout(5)
        try:
            packet = struct.pack("=IIII", self.PACKET_VERSION, 0, self.TYPE_NONE, 0)
            self.socket.sendall(packet)
            self.socket.recv(self.HEADER_SIZE)
        except:
            return False

        processes = await self.get_process_list()
        smt_process_id = \
            [process.process_id for process in processes if process.title_id.lower() == smt_title_id.lower()][
                0]
        await self.connect_to_process(smt_process_id)

        return True

    def _read_single(self, address: int, size: int) -> bytes:
        out_packet = struct.pack("=IIIIII", self.PACKET_VERSION, 0, self.TYPE_READ, 8, address, size)
        self.socket.sendall(out_packet)
        in_packet = self.socket.recv(self.HEADER_SIZE + self.MAX_READ_SIZE)
        if in_packet and len(in_packet) == self.HEADER_SIZE + size:
            return in_packet[self.HEADER_SIZE:]
        else:
            raise Exception("Did not receive packet of expected size.")

    async def read(self, address: int, size: int) -> bytes:
        try:
            mem = b""
            while size > 0:
                request_size = min(size, self.MAX_READ_SIZE)
                mem += self._read_single(address, request_size)
                address += request_size
                size -= request_size
            return mem
        except Exception as e:
            raise AzaharException(f"Lost connection to emulator ({str(e)})")

    async def read_u32(self, address: int) -> int:
        return int.from_bytes(await self.read(address, 4), "little")

    def _write_single(self, address: int, data: bytes) -> None:
        out_packet = struct.pack("=IIIIII", self.PACKET_VERSION, 0, self.TYPE_WRITE, 8 + len(data), address, len(data))
        out_packet += data
        self.socket.sendall(out_packet)
        self.socket.recv(self.HEADER_SIZE)

    async def write(self, address: int, data: bytes) -> None:
        try:
            start = 0
            while start < len(data):
                end = min(start + self.MAX_WRITE_SIZE, len(data))
                self._write_single(address + start, data[start:end])
                start += self.MAX_WRITE_SIZE
        except Exception as e:
            raise AzaharException(f"Lost connection to emulator ({str(e)})")

    async def write_u32(self, address: int, value: int) -> None:
        await self.write(address, value.to_bytes(4, "little"))

    async def get_process_list(self):
        start_index = 0
        max_amount = 100
        packet_size = 8

        out_packet = struct.pack("=IIIIII", self.PACKET_VERSION, 0, self.TYPE_PROCESS_LIST, packet_size, start_index,
                                 max_amount)
        self.socket.sendall(out_packet)
        in_packet = self.socket.recv(1000)
        in_packet_size = len(in_packet)

        struct_format = "<IQ8s"
        struct_size = struct.calcsize(struct_format)

        byte_offset = 0
        processes = []

        while byte_offset < in_packet_size:
            struct_end = byte_offset + struct_size
            packet_slice = in_packet[byte_offset:struct_end]
            process_id, title_id_int, _ = struct.unpack(struct_format, packet_slice)
            title_id = hex(title_id_int)
            process = ProcessInfo(process_id, title_id)

            processes.append(process)

            byte_offset += struct_size

        return processes

    async def connect_to_process(self, process_id: int):
        operation = 1
        packet_size = 8
        out_packet = struct.pack("=IIIIII", self.PACKET_VERSION, 0, self.TYPE_SET_GET_PROCESS, packet_size, operation,
                                 process_id)

        self.socket.sendall(out_packet)
        self.socket.recv(self.HEADER_SIZE)


azahar = AzaharInterface()
asyncio.run(azahar.connect())
