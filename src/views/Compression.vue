<template>
    <!-- 上传区域 -->
    <div class="bg-white rounded-lg shadow-sm p-8 mb-6">
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
            @dragover.prevent @drop.prevent="handleDrop" @click="triggerFileInput">
            <input type="file" ref="fileInput" class="hidden" multiple @change="handleFileChange" />
            <i class="fas fa-cloud-upload-alt text-5xl text-gray-400 mb-4"></i>
            <p class="text-gray-600">拖拽文件到此处或点击上传</p>
            <p class="text-gray-400 text-sm mt-2">支持 ZIP、RAR、7Z 等压缩文件格式</p>
        </div>
    </div>
    <!-- 文件列表 -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-medium">文件列表</h2>
            <div class="flex space-x-2">
                <button class="px-4 py-2 bg-blue-500 text-white !rounded-button whitespace-nowrap hover:bg-blue-600">
                    全部压缩
                </button>
                <button class="px-4 py-2 border border-gray-300 !rounded-button whitespace-nowrap hover:bg-gray-50">
                    清空列表
                </button>
            </div>
        </div>
        <div class="space-y-4">
            <div v-for="file in fileList" :key="file.id"
                class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-file-archive text-blue-500 text-xl"></i>
                    <div>
                        <p class="font-medium">{{ file.name }}</p>
                        <p class="text-sm text-gray-500">{{ file.size }}</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="w-32">
                        <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500 transition-all duration-300"
                                :style="{ width: `${file.progress}%` }"></div>
                        </div>
                    </div>
                    <span class="text-sm text-gray-600">{{ file.progress }}%</span>
                    <button class="text-red-500 hover:text-red-600">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
    <!-- AI 分析结果 -->
    <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-lg font-medium mb-4">AI 分析建议</h2>
        <div class="space-y-4">
            <!-- 思考状态 -->
            <div class="p-4 bg-gray-50 rounded-lg flex justify-between items-center">
                <span class="text-gray-600">正在思考</span>
                <i class="fas fa-circle-notch fa-spin text-blue-500"></i>
            </div>
            <!-- 生成状态 -->
            <div class="p-4 bg-gray-50 rounded-lg flex justify-between items-center">
                <span class="text-gray-600">正在生成压缩方案</span>
                <i class="fas fa-circle-notch fa-spin text-blue-500"></i>
            </div>
            <!-- 实时输出 -->
            <div class="p-6 bg-blue-50 rounded-lg border border-blue-100">
                <pre class="text-gray-700 font-mono text-sm leading-relaxed whitespace-pre-wrap">{{ streamText }}</pre>
                <div v-if="isStreaming" class="mt-3 flex items-center text-blue-500">
                    <i class="fas fa-circle-notch fa-spin mr-2"></i>
                    <span class="text-sm">正在分析...</span>
                </div>
            </div>
            <!-- 压缩方案列表 -->
            <div v-for="(result, index) in aiResults" :key="index" class="p-4 bg-blue-50 rounded-lg">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="font-medium text-blue-700">{{ result.title }}</h3>
                        <p class="text-gray-600 mt-2">{{ result.description }}</p>
                    </div>
                    <div class="flex space-x-2">
                        <button
                            class="px-4 py-2 bg-blue-500 text-white !rounded-button whitespace-nowrap hover:bg-blue-600">
                            应用方案
                        </button>
                        <button
                            class="px-4 py-2 border border-gray-300 !rounded-button whitespace-nowrap hover:bg-gray-50"
                            @click="showEditDialog = true">
                            编辑方案
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- 编辑压缩方案弹窗 -->
    <div v-if="showEditDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg w-[600px] shadow-xl">
            <div class="p-6 border-b border-gray-200">
                <div class="flex justify-between items-center">
                    <h3 class="text-lg font-medium">编辑压缩方案</h3>
                    <button class="text-gray-400 hover:text-gray-600" @click="showEditDialog = false">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="p-6">
                <div class="space-y-4">
                    <div v-for="file in fileList" :key="file.id" class="p-4 bg-gray-50 rounded-lg">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-3">
                                <i class="fas fa-file-archive text-blue-500"></i>
                                <div>
                                    <p class="font-medium">{{ file.name }}</p>
                                    <p class="text-sm text-gray-500">{{ file.size }}</p>
                                </div>
                            </div>
                            <div class="w-48">
                                <div class="relative">
                                    <button @click="file.showAlgorithmList = !file.showAlgorithmList"
                                        class="w-full px-4 py-2 text-left bg-white border border-gray-300 rounded-lg flex items-center justify-between !rounded-button">
                                        <span>{{ file.selectedAlgorithm || '选择算法' }}</span>
                                        <i class="fas fa-chevron-down text-gray-400"></i>
                                    </button>
                                    <div v-if="file.showAlgorithmList"
                                        class="absolute w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                                        <div class="py-1">
                                            <button v-for="algo in compressionAlgorithms" :key="algo.value"
                                                @click="selectAlgorithm(file, algo.value)"
                                                class="w-full px-4 py-2 text-left hover:bg-gray-50 !rounded-button">
                                                {{ algo.label }}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="p-6 border-t border-gray-200 flex justify-end space-x-4">
                <button class="px-4 py-2 border border-gray-300 !rounded-button whitespace-nowrap hover:bg-gray-50"
                    @click="showEditDialog = false">
                    取消
                </button>
                <button class="px-4 py-2 bg-blue-500 text-white !rounded-button whitespace-nowrap hover:bg-blue-600"
                    @click="applyCompressionSettings">
                    确定
                </button>
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import { ref, onUnmounted, reactive, computed } from 'vue';
// 组件逻辑将在这里实现
const fileInput = ref<HTMLInputElement | null>(null);
const showEditDialog = ref(false);
const compressionAlgorithms = [
    { value: 'zstd', label: 'Zstandard (高压缩比)' },
    { value: 'lzma2', label: 'LZMA2 (超高压缩比)' },
    { value: 'lz4', label: 'LZ4 (快速压缩)' },
    { value: 'deflate', label: 'Deflate (通用压缩)' },
    { value: 'bzip2', label: 'BZip2 (高压缩比)' }
];
const fileList = ref([
    {
        id: 1,
        name: '项目文档集合.zip',
        size: '2.5 GB',
        progress: 75,
        showAlgorithmList: false,
        selectedAlgorithm: ''
    },
    {
        id: 2,
        name: '产品设计资源.rar',
        size: '1.8 GB',
        progress: 90,
        showAlgorithmList: false,
        selectedAlgorithm: ''
    },
    {
        id: 3,
        name: '视频素材备份.7z',
        size: '4.2 GB',
        progress: 30,
        showAlgorithmList: false,
        selectedAlgorithm: ''
    }
]);
// 选择压缩算法
const selectAlgorithm = (file: any, algorithm: string) => {
    file.selectedAlgorithm = algorithm;
    file.showAlgorithmList = false;
};
// 应用压缩设置
const applyCompressionSettings = () => {
    // 这里可以处理压缩设置的保存逻辑
    showEditDialog.value = false;
    // 重置下拉列表状态
    fileList.value.forEach(file => {
        file.showAlgorithmList = false;
    });
};
const aiResults = [
    {
        title: '推荐压缩方案 A',
        description: '使用 ZSTD 算法进行压缩，预计可节省 60% 存储空间，适用于当前上传的文档类型文件。压缩后预计文件大小约为 1.0 GB。'
    },
    {
        title: '推荐压缩方案 B',
        description: '采用分块压缩策略，每块大小设置为 128MB，可实现并行处理提升压缩速度。预计耗时 5 分钟，压缩率可达 70%。'
    }
];
const triggerFileInput = () => {
    fileInput.value?.click();
};
const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files) {
        // 处理文件上传逻辑
    }
};
const handleDrop = (event: DragEvent) => {
    const files = event.dataTransfer?.files;
    if (files) {
        // 处理拖拽上传逻辑
    }
};
const streamText = ref('');
const isStreaming = ref(false);
let streamInterval: number | null = null;
const startStreamText = () => {
    if (isStreaming.value) return;
    isStreaming.value = true;
    streamText.value = '';
    const fullText = `📂 开始分析文件结构...
    ✨ 初步分析结果
    • 检测到多层级目录结构
    • 文件类型分布：文档 60%、图片 30%、其他 10%
    🔍 压缩策略评估
    • 文档文件：建议使用 LZMA2 高压缩算法
    • 图片文件：采用智能存储模式
    • 执行方式：启用多线程并行压缩
    📊 预期效果分析
    • 预计压缩率：65%
    • 预计耗时：3-5 分钟
    • 系统资源：CPU 75%，内存约 2GB
    💡 优化建议
    • 建议清理可能存在的冗余数据
    • 文件去重可提升压缩效果
    🎯 正在生成详细压缩方案...`;
    let currentIndex = 0;
    streamInterval = window.setInterval(() => {
        if (currentIndex < fullText.length) {
            streamText.value += fullText[currentIndex];
            currentIndex++;
        } else {
            if (streamInterval) {
                clearInterval(streamInterval);
                streamInterval = null;
            }
            isStreaming.value = false;
        }
    }, 50);
};
// 启动文本流
startStreamText();
onUnmounted(() => {
    if (streamInterval) {
        clearInterval(streamInterval);
    }
});
onUnmounted(() => {
    if (streamInterval) {
        clearInterval(streamInterval);
    }
});
</script>
<style scoped></style>
