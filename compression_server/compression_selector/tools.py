"""
统一压缩算法接口类
用法：
1. 选择算法：compressor = GZipCompressor()
2. 压缩文件：compressed_file = compressor.compress("input.txt", "output.gz")
3. 解压文件：decompressed_file = compressor.decompress("output.gz", "decompressed.txt")
"""

import bz2
import gzip
import lzma
import os
import tarfile
import zipfile
import zlib
from abc import ABC, abstractmethod
from typing import Dict

import blosc
import brotli
import lz4.frame
import lzo
import py7zr
import snappy
import zstandard as zstd
from PIL import Image
from pydub import AudioSegment
from zopfli.zlib import compress as zopfli_compress


# 第三方库需安装：pip install lz4 python-snappy brotli python-lzo zopfli py7zr zstandard blosc




class BaseCompressor(ABC):
    """压缩算法基类"""

    @abstractmethod
    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        pass

    @abstractmethod
    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        pass

    @staticmethod
    def _read_bytes(input_path: str) -> bytes:
        with open(input_path, 'rb') as f:
            return f.read()

    @staticmethod
    def _write_bytes(output_path: str, data: bytes):
        with open(output_path, 'wb') as f:
            f.write(data)

class Compressor(object):

    def __init__(self):
        self.registry: Dict[str, BaseCompressor] = {}

    def register(self, name:str, compress:BaseCompressor):
        self.registry[name] = compress

    def compression_list(self):
        return list(self.registry.keys())

register = Compressor()


def register_compression(name=None):
    """装饰器工厂：允许自定义注册键"""
    def decorator(cls):
        register.register(name, cls())
        return cls
    return decorator



# ------------------- 无损压缩算法 -------------------
@register_compression("DEFLATE/zlib")
class ZlibCompressor(BaseCompressor):
    """DEFLATE/zlib 压缩"""

    def compress(self, input_path: str, output_path: str, level: int = zlib.Z_BEST_COMPRESSION, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = zlib.compress(data, level=level)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = zlib.decompress(compressed)
        self._write_bytes(output_path, data)
        return output_path

@register_compression("GZIP")
class GZipCompressor(BaseCompressor):
    """GZIP 压缩"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        with open(input_path, 'rb') as f_in, gzip.open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        with gzip.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
        return output_path

@register_compression("BZip2")
class BZip2Compressor(BaseCompressor):
    """BZip2 压缩"""

    def compress(self, input_path: str, output_path: str, level: int = 9, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = bz2.compress(data, compresslevel=level)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = bz2.decompress(compressed)
        self._write_bytes(output_path, data)
        return output_path

@register_compression("LZMA/XZ")
class LZMACompressor(BaseCompressor):
    """LZMA/XZ 压缩"""

    def compress(self, input_path: str, output_path: str, preset: int = 9, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = lzma.compress(data, preset=preset)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = lzma.decompress(compressed)
        self._write_bytes(output_path, data)
        return output_path

@register_compression("LZ4")
class LZ4Compressor(BaseCompressor):
    """LZ4 压缩"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = lz4.frame.compress(data)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = lz4.frame.decompress(compressed)
        self._write_bytes(output_path, data)
        return output_path

@register_compression("ZStandard")
class ZstdCompressor(BaseCompressor):
    """ZStandard 压缩"""

    def compress(self, input_path: str, output_path: str, level: int = 3, **kwargs) -> str:
        cctx = zstd.ZstdCompressor(level=level)
        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            cctx.copy_stream(f_in, f_out)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        dctx = zstd.ZstdDecompressor()
        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            dctx.copy_stream(f_in, f_out)
        return output_path

@register_compression("Snappy")
class SnappyCompressor(BaseCompressor):
    """Snappy 压缩"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = snappy.compress(data)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = snappy.decompress(compressed)
        self._write_bytes(output_path, data)
        return output_path

@register_compression("Brotli")
class BrotliCompressor(BaseCompressor):
    """Brotli 压缩"""

    def compress(self, input_path: str, output_path: str, mode: int = brotli.MODE_TEXT, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = brotli.compress(data, mode=mode)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = brotli.decompress(compressed)
        self._write_bytes(output_path, data)
        return output_path

@register_compression("LZO")
class LZOCompressor(BaseCompressor):
    """LZO 压缩"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = lzo.compress(data)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = lzo.decompress(compressed)
        self._write_bytes(output_path, data)
        return output_path

@register_compression("Zopfli")
class ZopfliCompressor(BaseCompressor):
    """Zopfli (优化DEFLATE) 压缩"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        data = self._read_bytes(input_path)
        compressed = zopfli_compress(data)
        self._write_bytes(output_path, compressed)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        compressed = self._read_bytes(input_path)
        data = zlib.decompress(compressed)  # 使用标准 zlib 解压
        self._write_bytes(output_path, data)
        return output_path


# ------------------- 归档格式 -------------------
class ZipCompressor(BaseCompressor):
    """ZIP 归档"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(input_path, arcname=os.path.basename(input_path))
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        with zipfile.ZipFile(input_path, 'r') as zipf:
            zipf.extractall(os.path.dirname(output_path))
        return output_path


class SevenZipCompressor(BaseCompressor):
    """7-Zip 归档"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        with py7zr.SevenZipFile(output_path, 'w') as archive:
            archive.write(input_path, os.path.basename(input_path))
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        with py7zr.SevenZipFile(input_path, 'r') as archive:
            archive.extractall(os.path.dirname(output_path))
        return output_path


class TarGzCompressor(BaseCompressor):
    """Tar + GZIP 压缩"""

    def compress(self, input_path: str, output_path: str, **kwargs) -> str:
        with tarfile.open(output_path, 'w:gz') as tar:
            tar.add(input_path, arcname=os.path.basename(input_path))
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        with tarfile.open(input_path, 'r:gz') as tar:
            tar.extractall(os.path.dirname(output_path))
        return output_path


# ------------------- 有损压缩 -------------------
@register_compression("WebP")
class WebPCompressor(BaseCompressor):
    """WebP 图像压缩"""

    def compress(self, input_path: str, output_path: str, quality: int = 80, **kwargs) -> str:
        img = Image.open(input_path)
        img.save(output_path, 'WEBP', quality=quality)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        raise NotImplementedError("有损压缩不支持无损解压")

@register_compression("MP3")
class MP3Compressor(BaseCompressor):
    """MP3 音频压缩"""

    def compress(self, input_path: str, output_path: str, bitrate: str = '128k', **kwargs) -> str:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format='mp3', bitrate=bitrate)
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        raise NotImplementedError("有损压缩不支持无损解压")

# ------------------- 使用示例 -------------------
if __name__ == '__main__':
    print(register.registry)