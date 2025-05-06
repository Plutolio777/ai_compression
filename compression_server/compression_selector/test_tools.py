import os
import tempfile
import unittest
from .tools import *

class TestBaseCompressor(unittest.TestCase):
    """测试基类，提供通用工具方法"""
    
    compressor = None
    def setUp(self):
        # 创建临时测试文件
        self.test_dir = os.path.join("test_data", f"{self.compressor.__class__.__name__}")
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.input_file = os.path.join(self.test_dir, "test_input.txt")
        self.compressed_file = os.path.join(self.test_dir, "compressed")
        self.decompressed_file = os.path.join(self.test_dir, "decompressed.txt")
        
        # 写入测试数据
        with open(self.input_file, "wb") as f:
            f.write(b"This is a test file content. " * 100)  # 生成足够大的测试数据
    
    def tearDown(self):
        # 清理临时目录及其所有内容
        # import shutil
        # if os.path.exists(self.test_dir):
        #     shutil.rmtree(self.test_dir)
        pass
    
    def assertFileExists(self, path):
        self.assertTrue(os.path.exists(path), f"File {path} does not exist")
    
    def assertFileContentEqual(self, file1, file2):
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            self.assertEqual(f1.read(), f2.read(), "File contents differ")

class TestZlibCompressor(TestBaseCompressor):
    compressor = ZlibCompressor()
    
    def test_compress_decompress(self):
        # 测试压缩
        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file)
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file)
        self.assertFileExists(self.compressed_file)
        
        # 计算并打印压缩比
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file)
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")
        self.assertLess(compressed_size, original_size)
        
        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}")
        result = self.compressor.decompress(self.compressed_file, self.decompressed_file)
        print(f"解压文件: {result}")
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)
        
        # 验证解压后内容与原始内容一致
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestGZipCompressor(TestBaseCompressor):
    compressor = GZipCompressor()
    def test_compress_decompress(self):

        
        # 测试压缩
        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".gz")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".gz")
        self.assertFileExists(self.compressed_file + ".gz")
        
        # 计算并打印压缩比
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".gz")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")
        
        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}")
        result = self.compressor.decompress(self.compressed_file + ".gz", self.decompressed_file)
        print(f"解压文件: {result}")
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)
        
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestBZip2Compressor(TestBaseCompressor):
    compressor = BZip2Compressor()
    def test_compress_decompress(self):
        
        
        # 测试压缩
        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".bz2")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".bz2")
        self.assertFileExists(self.compressed_file + ".bz2")
        
        # 计算并打印压缩比
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".bz2")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")

        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}")       
        result = self.compressor.decompress(self.compressed_file + ".bz2", self.decompressed_file)
        print(f"解压文件: {result}")
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)
        
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestLZMACompressor(TestBaseCompressor):
    compressor = LZMACompressor()
    def test_compress_decompress(self):
        
        
        # 测试压缩
        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".xz")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".xz")
        self.assertFileExists(self.compressed_file + ".xz")
        
        # 计算并打印压缩比
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".xz")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")
        
        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}")               
        result = self.compressor.decompress(self.compressed_file + ".xz", self.decompressed_file)
        print(f"解压文件: {result}")       
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)
        
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestLZ4Compressor(TestBaseCompressor):
    compressor = LZ4Compressor()
    def test_compress_decompress(self):
        
        
        # 测试压缩
        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".lz4")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".lz4")
        self.assertFileExists(self.compressed_file + ".lz4")
        
        # 计算并打印压缩比
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".lz4")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")

        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}")  
        result = self.compressor.decompress(self.compressed_file + ".lz4", self.decompressed_file)
        print(f"解压文件: {result}")    
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)
        
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestZstdCompressor(TestBaseCompressor):
    compressor = ZstdCompressor()
    def test_compress_decompress(self):
        
        
        # 测试压缩
        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".zst")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".zst")
        self.assertFileExists(self.compressed_file + ".zst")
        
        # 计算并打印压缩比
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".zst")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")

        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}")     
        result = self.compressor.decompress(self.compressed_file + ".zst", self.decompressed_file)
        print(f"解压文件: {result}") 
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)
        
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestSnappyCompressor(TestBaseCompressor):
    compressor = SnappyCompressor()
    def test_compress_decompress(self):
        
        
        # 测试压缩
        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".snappy")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".snappy")
        self.assertFileExists(self.compressed_file + ".snappy")
        
        # 计算并打印压缩比
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".snappy")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")

        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}")  
        result = self.compressor.decompress(self.compressed_file + ".snappy", self.decompressed_file)
        print(f"解压文件: {result}") 
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)
        
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestBrotliCompressor(TestBaseCompressor):
    compressor = BrotliCompressor()
    def test_compress_decompress(self):
        

        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".br")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".br")
        self.assertFileExists(self.compressed_file + ".br")

        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".br")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")

        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}") 
        result = self.compressor.decompress(self.compressed_file + ".br", self.decompressed_file)
        print(f"解压文件: {result}")
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)

        self.assertFileContentEqual(self.input_file, self.decompressed_file)


class TestLZOCompressor(TestBaseCompressor):
    compressor = LZOCompressor()
    def test_compress_decompress(self):
        

        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".lzo")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".lzo")
        self.assertFileExists(self.compressed_file + ".lzo")

        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".lzo")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")

        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}") 
        result = self.compressor.decompress(self.compressed_file + ".lzo", self.decompressed_file)
        print(f"解压文件: {result}")
        self.assertEqual(result, self.decompressed_file)
        self.assertFileExists(self.decompressed_file)

        self.assertFileContentEqual(self.input_file, self.decompressed_file)

# class TestWebPCompressor(TestBaseCompressor):
#     def setUp(self):
#         # 创建临时测试图片文件
#         self.test_dir = tempfile.mkdtemp()
#         self.input_file = os.path.join(self.test_dir, "test_input.png")
#         self.compressed_file = os.path.join(self.test_dir, "compressed.webp")
        
#         # 创建一个简单的测试图片
#         from PIL import Image
#         img = Image.new('RGB', (100, 100), color='red')
#         img.save(self.input_file, 'PNG')
    
#     def test_compress(self):
#         compressor = WebPCompressor()
        
#         result = compressor.compress(self.input_file, self.compressed_file, quality=80)
#         self.assertEqual(result, self.compressed_file)
#         self.assertFileExists(self.compressed_file)
        
#         # 验证压缩文件比原始文件小
#         original_size = os.path.getsize(self.input_file)
#         compressed_size = os.path.getsize(self.compressed_file)
#         self.assertLess(compressed_size, original_size)


class TestZipCompressor(TestBaseCompressor):
    compressor = ZipCompressor()
    def test_compress_decompress(self):
        

        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".zip")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".zip")
        self.assertFileExists(self.compressed_file + ".zip")
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".zip")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")
        
        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}") 
        result = self.compressor.decompress(self.compressed_file + ".zip", self.decompressed_file)
        print(f"解压目录: {self.decompressed_file}")
        self.assertFileContentEqual(self.input_file, self.decompressed_file)


class TestSevenZipCompressor(TestBaseCompressor):
    compressor = SevenZipCompressor()
    def test_compress_decompress(self):

        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".7z")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".7z")
        self.assertFileExists(self.compressed_file + ".7z")
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".7z")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")
        
        # 测试解压
        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}") 
        result = self.compressor.decompress(self.compressed_file + ".7z", self.decompressed_file)
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

class TestTarGzCompressor(TestBaseCompressor):
    compressor = TarGzCompressor()
    def test_compress_decompress(self):


        print(f"\n压缩测试 - {self.compressor.__class__.__name__}")
        print(f"原始文件: {self.input_file}")
        result = self.compressor.compress(self.input_file, self.compressed_file + ".tar.gz")
        print(f"压缩文件: {result}")
        self.assertEqual(result, self.compressed_file + ".tar.gz")
        self.assertFileExists(self.compressed_file + ".tar.gz")
        original_size = os.path.getsize(self.input_file)
        compressed_size = os.path.getsize(self.compressed_file + ".tar.gz")
        ratio = original_size / compressed_size
        print(f"压缩比: {ratio:.2f}:1 (原始大小: {original_size} bytes, 压缩后: {compressed_size} bytes)")

        print(f"\n解压测试 - {self.compressor.__class__.__name__}")
        print(f"压缩文件: {self.compressed_file}") 
        result = self.compressor.decompress(self.compressed_file + ".tar.gz", self.decompressed_file)
        self.assertFileContentEqual(self.input_file, self.decompressed_file)

if __name__ == '__main__':
    unittest.main()
