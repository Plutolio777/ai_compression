"""
统一压缩算法接口类
用法：
1. 选择算法：compressor = GZipCompressor()
2. 压缩文件：compressed_file = compressor.compress("input.txt", "output.gz")
3. 解压文件：decompressed_file = compressor.decompress("output.gz", "decompressed.txt")
"""
import io
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

    @abstractmethod
    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return self.compress_data(data, **kwargs)

    @abstractmethod
    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed_data = self._read_bytes(input_path)
        return self.decompress_data(compressed_data, **kwargs)

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

    def register(self, name: str, compress: BaseCompressor):
        self.registry[name] = compress

    def compression_list(self):
        return list(self.registry.keys())

    def compress_bytes(self, key, input_path: str, **kwargs) -> bytes:
        return self.registry.get(key, "None").compress_bytes(input_path, **kwargs)

    def decompress_bytes(self, key, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        return self.registry.get(key, "None").decompress_bytes(input_path, **kwargs)


register = Compressor()


def register_compression(name=None, prefix=""):
    """装饰器工厂：允许自定义注册键"""

    def decorator(cls):
        register.register(name, cls())
        return cls

    return decorator


# ------------------- 无损压缩算法 -------------------
@register_compression("DEFLATE/zlib", ".zlib")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return zlib.compress(data, level=kwargs.get('level', zlib.Z_BEST_COMPRESSION))

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return zlib.decompress(compressed)


@register_compression("GZIP", ".gzip")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return self.compress_data(data, **kwargs)

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return self.decompress_data(compressed, **kwargs)


@register_compression("BZip2", ".gzip2")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return bz2.compress(data, compresslevel=kwargs.get('level', 9))

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return bz2.decompress(compressed)


@register_compression("LZMA/XZ", ".lzma")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return lzma.compress(data, preset=kwargs.get('preset', 9))

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return lzma.decompress(compressed)


@register_compression("LZ4", ".lz4")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return lz4.frame.compress(data)

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return lz4.frame.decompress(compressed)


@register_compression("ZStandard", ".zstandard")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        cctx = zstd.ZstdCompressor(level=kwargs.get('level', 3))
        return cctx.compress(data)

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        dctx = zstd.ZstdDecompressor()
        return dctx.decompress(compressed)


@register_compression("Snappy", ".snappy")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return snappy.compress(data)

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return snappy.decompress(compressed)


@register_compression("Brotli", ".brotli")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return brotli.compress(data, mode=kwargs.get('mode', brotli.MODE_TEXT))

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return brotli.decompress(compressed)


@register_compression("LZO", ".lzo")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return lzo.compress(data)

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return lzo.decompress(compressed)


@register_compression("Zopfli", ".zopfli")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        return zopfli_compress(data)

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        return zlib.decompress(compressed)


# ------------------- 归档格式 -------------------
@register_compression("Zip")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(os.path.basename(input_path), data)
        return buf.getvalue()

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        buf = io.BytesIO(compressed)
        with zipfile.ZipFile(buf, 'r') as zipf:
            return zipf.read(zipf.namelist()[0])


@register_compression("7-Zip")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        print(input_path)
        data = self._read_bytes(input_path)
        buf = io.BytesIO()
        # 在内存中创建7z文件，并写入文件数据
        with py7zr.SevenZipFile(buf, 'w') as archive:
            # 使用os.path.basename(input_path)来获取文件名，并将文件数据写入
            archive.writestr(data, os.path.basename(input_path))
        return buf.getvalue()

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        with io.BytesIO(data) as input_buf:
            with py7zr.SevenZipFile(input_buf, mode='r') as archive:
                extracted = archive.readall()
        result_bytes = b''
        for fileobj in extracted.values():
            result_bytes += fileobj.read()
        return result_bytes


@register_compression("TarGz")
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

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        data = self._read_bytes(input_path)
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode='w:gz') as tar:
            info = tarfile.TarInfo(name=os.path.basename(input_path))
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        return buf.getvalue()

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        compressed = self._read_bytes(input_path)
        buf = io.BytesIO(compressed)
        with tarfile.open(fileobj=buf, mode='r:gz') as tar:
            member = tar.getmembers()[0]
            return tar.extractfile(member).read()


@register_compression("None")
class NoneCompressor(BaseCompressor):
    """无需压缩 音频压缩"""

    def compress(self, input_path: str, output_path: str, bitrate: str = '128k', **kwargs) -> str:
        self._write_bytes(output_path, self._read_bytes(input_path))
        return output_path

    def decompress(self, input_path: str, output_path: str, **kwargs) -> str:
        self._write_bytes(output_path, self._read_bytes(input_path))
        return output_path

    def compress_bytes(self, input_path: str, **kwargs) -> bytes:
        """压缩文件并返回bytes数据"""
        return self._read_bytes(input_path)

    def decompress_bytes(self, input_path: str, **kwargs) -> bytes:
        """解压文件并返回bytes数据"""
        return self._read_bytes(input_path)


# ------------------- 使用示例 -------------------
if __name__ == '__main__':
    print(register.registry)
