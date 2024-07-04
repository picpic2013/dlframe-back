import struct
from dataclasses import dataclass

@dataclass
class Pkt:
    from_addr: str
    to_addr: str
    data: bytes
    ttl: int

    def __init__(self, from_addr, to_addr, data, ttl=7) -> None:
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.data = data
        self.ttl = ttl

    def to_binary(self):
        from_addr_bytes = self.from_addr.encode("utf-8")
        to_addr_bytes = self.to_addr.encode("utf-8")

        return struct.pack(
            f'IIII{len(from_addr_bytes)}s{len(to_addr_bytes)}s{len(self.data)}s', 
            len(from_addr_bytes), 
            len(to_addr_bytes), 
            len(self.data), 
            self.ttl, 
            from_addr_bytes, 
            to_addr_bytes, 
            self.data
        )
    
    @classmethod
    def from_binary(cls, data):
        from_addr_len, to_addr_len, data_len, ttl = struct.unpack('IIII', data[:16])
        from_addr, to_addr, data = struct.unpack(f'16x{from_addr_len}s{to_addr_len}s{data_len}s', data)
        return cls(from_addr.decode("utf-8"), to_addr.decode("utf-8"), data, ttl)
    
    def __str__(self) -> str:
        return f'[ "{self.from_addr}" -> "{self.to_addr}" ( {self.ttl} ) ]: {self.data}'