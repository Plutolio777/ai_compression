<template>
    <!-- 顶部工具栏 -->
    <div class="bg-white p-4 shadow-sm sticky top-16 z-10 w-full">
        <div class="flex items-center justify-between px-8">
            <div class="flex items-center space-x-4">
                <button
                    @click="showCreateFolderModal = true"
                    class="!rounded-button flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white hover:bg-blue-600">
                    <i class="fas fa-folder-plus"></i>
                    <span>新建文件夹</span>
                </button>
                <button
                    @click="showUploadModal = true"
                    class="!rounded-button flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white hover:bg-blue-600">
                    <i class="fas fa-upload"></i>
                    <span>上传</span>
                </button>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-search text-gray-400"></i>
                    </div>
                    <input type="text"
                        class="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="搜索文件..." v-model="searchQuery" />
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <button class="!rounded-button p-2 text-gray-600 hover:bg-gray-100"
                    :class="{ 'text-blue-500': viewMode === 'grid' }" @click="viewMode = 'grid'">
                    <i class="fas fa-th-large"></i>
                </button>
                <button class="!rounded-button p-2 text-gray-600 hover:bg-gray-100"
                    :class="{ 'text-blue-500': viewMode === 'list' }" @click="viewMode = 'list'">
                    <i class="fas fa-list"></i>
                </button>
            </div>
        </div>
    </div>
    <!-- 主内容区 -->
    <div class="flex p-6">
        <!-- 文件列表 -->
        <div class="flex-1 p-6">
            <!-- 面包屑导航 -->
            <div class="mb-4 flex items-center space-x-2 text-sm text-gray-600">
                <button class="hover:text-blue-500" @click="currentPath = []">
                    <i class="fas fa-home"></i>
                </button>
                <button v-if="currentPath.length > 0" 
                    class="hover:text-blue-500 ml-2" 
                    @click="currentPath = currentPath.slice(0, -1)">
                    <i class="fas fa-arrow-left"></i>
                </button>
                <template v-for="(folder, index) in currentPath" :key="index">
                    <i class="fas fa-chevron-right text-gray-400"></i>
                    <button class="hover:text-blue-500" @click="navigateTo(index)">
                        {{ folder }}
                    </button>
                </template>
            </div>
            <!-- 网格视图 -->
            <div v-if="viewMode === 'grid'" class="grid grid-cols-6 gap-4">
                    <div v-for="file in filteredFiles" :key="file.id"
                        class="relative group bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                        :class="{ 'ring-2 ring-blue-500': selectedFiles.includes(file.id) }"
                        @click="toggleFileSelection(file.id)" 
                        @dblclick="handleFileDoubleClick(file)"
                        @contextmenu.prevent="showContextMenu($event, file)">
                    <div class="flex flex-col items-center">
                        <div class="w-16 h-16 mb-2 flex items-center justify-center">
                            <i :class="getFileIcon(file.type)" class="text-4xl"
                                :style="{ color: getFileColor(file.type) }"></i>
                        </div>
                        <p class="text-sm text-center font-medium truncate w-full">{{ file.name }}</p>
                        <p class="text-xs text-gray-500">{{ file.size }}</p>
                    </div>
                    <div class="absolute top-2 right-2 flex space-x-1">
                        <span v-if="file.important"
                            class="px-1.5 py-0.5 text-xs bg-red-100 text-red-600 rounded">重要</span>
                        <span v-if="file.cold"
                            class="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">冷数据</span>
                    </div>
                </div>
            </div>
            <!-- 列表视图 -->
            <div v-else class="bg-white rounded-lg shadow-sm">
                <div class="grid grid-cols-12 gap-4 p-4 text-sm font-medium text-gray-600 border-b">
                    <div class="col-span-6">名称</div>
                    <div class="col-span-2">大小</div>
                    <div class="col-span-2">修改时间</div>
                    <div class="col-span-2">标签</div>
                </div>
                <div class="divide-y">
                    <div v-for="file in filteredFiles" :key="file.id"
                        class="grid grid-cols-12 gap-4 p-4 hover:bg-gray-50 cursor-pointer items-center"
                        :class="{ 'bg-blue-50': selectedFiles.includes(file.id) }" 
                        @click="toggleFileSelection(file.id)"
                        @dblclick="handleFileDoubleClick(file)"
                        @contextmenu.prevent="showContextMenu($event, file)">
                        <div class="col-span-6 flex items-center space-x-3">
                            <i :class="getFileIcon(file.type)" :style="{ color: getFileColor(file.type) }"></i>
                            <span>{{ file.name }}</span>
                        </div>
                        <div class="col-span-2 text-gray-500">{{ file.size }}</div>
                        <div class="col-span-2 text-gray-500">{{ file.modifiedTime }}</div>
                        <div class="col-span-2 flex space-x-2">
                            <span v-if="file.important"
                                class="px-2 py-1 text-xs bg-red-100 text-red-600 rounded">重要</span>
                            <span v-if="file.cold"
                                class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">冷数据</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- 右侧操作面板 -->
        <div v-if="selectedFiles.length === 1" class="w-80 bg-white shadow-sm p-6 border-l">
            <div class="space-y-6">
                <!-- 预览 -->
                <div>
                    <h3 class="text-lg font-medium mb-4">文件预览</h3>
                    <div class="aspect-video bg-gray-100 rounded-lg flex items-center justify-center relative">
                        <div v-if="previewLoading" class="absolute inset-0 flex items-center justify-center">
                            <i class="fas fa-spinner fa-spin text-2xl text-blue-500"></i>
                        </div>
                        <template v-else>
                            <template v-if="previewError">
                                <div class="text-center p-4">
                                    <i class="fas fa-exclamation-triangle text-2xl text-red-500 mb-2"></i>
                                    <p class="text-sm text-gray-600">预览加载失败</p>
                                </div>
                            </template>
                            <template v-else>
                                <template v-if="selectedFileType === 'image'">
                                    <img :src="selectedFilePreview" class="max-w-full max-h-full object-contain" alt="预览图" />
                                </template>
                                <template v-else-if="selectedFileType === 'video'">
                                    <div class="relative w-full h-full">
                                        <i class="fas fa-play-circle text-4xl text-gray-400 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"></i>
                                        <img :src="selectedFilePreview" class="w-full h-full object-cover" alt="视频封面" />
                                    </div>
                                </template>
                                <template v-else-if="selectedFileType === 'pdf'">
                                    <div class="text-center p-4">
                                        <i class="fas fa-file-pdf text-4xl text-red-500 mb-2"></i>
                                        <p class="text-sm text-gray-600">PDF预览</p>
                                    </div>
                                </template>
                                <template v-else>
                                    <div class="text-center p-4">
                                        <i :class="getFileIcon(selectedFileType)" class="text-4xl" :style="{ color: getFileColor(selectedFileType) }"></i>
                                        <p class="text-sm text-gray-600 mt-2">不支持预览</p>
                                    </div>
                                </template>
                            </template>
                        </template>
                    </div>
                </div>
                <!-- 文件信息 -->
                <div>
                    <h3 class="text-lg font-medium mb-4">文件信息</h3>
                    <div class="space-y-3">
                        <div>
                            <p class="text-sm text-gray-500">存储路径</p>
                            <p class="text-sm font-medium">{{ selectedFilePath }}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">压缩信息</p>
                            <p class="text-sm font-medium">使用 ZSTD 算法，压缩率 65%</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">存储策略</p>
                            <p class="text-sm font-medium">标准存储</p>
                        </div>
                    </div>
                </div>
                <!-- 操作按钮 -->
                <div class="flex flex-col space-y-2">
                    <button class="!rounded-button w-full px-4 py-2 bg-blue-500 text-white hover:bg-blue-600">
                        下载文件
                    </button>
                    <button class="!rounded-button w-full px-4 py-2 border border-gray-300 hover:bg-gray-50">
                        生成分享链接
                    </button>
                    <button class="!rounded-button w-full px-4 py-2 border border-gray-300 hover:bg-gray-50">
                        移动到...
                    </button>
                    <button class="!rounded-button w-full px-4 py-2 border border-red-300 text-red-500 hover:bg-red-50">
                        删除
                    </button>
                </div>
            </div>
        </div>
    </div>
    <!-- 右键菜单 -->
    <div v-if="showMenu" class="fixed bg-white shadow-lg rounded-lg py-2 z-50"
        :style="{ top: menuPosition.y + 'px', left: menuPosition.x + 'px' }">
        <button class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm">
            <i class="fas fa-download mr-2"></i> 下载
        </button>
        <button class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm">
            <i class="fas fa-share-alt mr-2"></i> 分享
        </button>
        <button class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm">
            <i class="fas fa-tags mr-2"></i> 添加标签
        </button>
        <div class="border-t my-1"></div>
        <button class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm text-red-500">
            <i class="fas fa-trash-alt mr-2"></i> 删除
        </button>
    </div>

    <!-- 上传弹窗 -->
    <UploadModal 
      v-if="showUploadModal"
      :show="showUploadModal"
      :current-path="currentPath"
      @close="showUploadModal = false"
      @upload-success="handleUploadSuccess"
    />

    <!-- 新建文件夹弹窗 -->
    <CreateFolderModal
      v-if="showCreateFolderModal"
      :show="showCreateFolderModal"
      :current-path="currentPath"
      @close="showCreateFolderModal = false"
      @create-success="handleCreateFolderSuccess"
    />
</template>
<script lang="ts" setup>
import { ref, onUnmounted, reactive, computed } from 'vue';
import UploadModal from '../components/UploadModal.vue';
import CreateFolderModal from '../components/CreateFolderModal.vue';
import apiService from '../api/apiService';

const showUploadModal = ref(false);
const showCreateFolderModal = ref(false);
// 网盘功能相关数据
const viewMode = ref<'grid' | 'list'>('grid');
const searchQuery = ref('');
const currentPath = ref<string[]>([]);
const selectedFiles = ref<number[]>([]);
const showMenu = ref(false);
const menuPosition = ref({ x: 0, y: 0 });
const files = ref([
    {
        id: 1,
        name: '项目文档',
        type: 'folder',
        size: '-',
        modifiedTime: '2024-02-20 15:30',
        important: false,
        cold: false,
        children: [
            {
                id: 8,
                name: '需求文档.docx',
                type: 'doc',
                size: '1.2MB',
                modifiedTime: '2024-02-19 10:30',
                important: true,
                cold: false
            },
            {
                id: 9,
                name: '设计稿',
                type: 'folder',
                size: '-',
                modifiedTime: '2024-02-18 14:20',
                important: false,
                cold: false,
                children: [
                    {
                        id: 10,
                        name: 'UI设计.psd',
                        type: 'image',
                        size: '8.5MB',
                        modifiedTime: '2024-02-17 16:45',
                        important: false,
                        cold: false
                    }
                ]
            }
        ]
    },
    {
        id: 2,
        name: '设计资源',
        type: 'folder',
        size: '-',
        modifiedTime: '2024-02-19 09:45',
        important: false,
        cold: false,
        children: [
            {
                id: 11,
                name: '图标集.zip',
                type: 'archive',
                size: '45MB',
                modifiedTime: '2024-02-18 11:15',
                important: false,
                cold: true
            }
        ]
    },
    {
        id: 3,
        name: '项目方案.docx',
        type: 'doc',
        size: '2.5MB',
        modifiedTime: '2024-02-20 15:30',
        important: true,
        cold: false
    },
    {
        id: 4,
        name: '产品设计稿.psd',
        type: 'image',
        size: '15MB',
        modifiedTime: '2024-02-19 09:45',
        important: false,
        cold: false
    },
    {
        id: 5,
        name: '演示视频.mp4',
        type: 'video',
        size: '256MB',
        modifiedTime: '2024-02-18 16:20',
        important: false,
        cold: true
    },
    {
        id: 6,
        name: '源代码备份.zip',
        type: 'archive',
        size: '128MB',
        modifiedTime: '2024-02-17 11:15',
        important: true,
        cold: false
    },
    {
        id: 7,
        name: '会议记录.pdf',
        type: 'pdf',
        size: '1.2MB',
        modifiedTime: '2024-02-16 14:50',
        important: false,
        cold: true
    }
]);
const getCurrentLevelFiles = () => {
    let currentFiles = files.value;
    for (const folderName of currentPath.value) {
        const folder = currentFiles.find(f => f.type === 'folder' && f.name === folderName);
        if (folder && folder.children) {
            currentFiles = folder.children;
        } else {
            return [];
        }
    }
    return currentFiles;
};

const filteredFiles = computed(() => {
    const currentFiles = getCurrentLevelFiles();
    if (!searchQuery.value) return currentFiles;
    return currentFiles.filter(file =>
        file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
});
const selectedFileType = computed(() => {
    if (selectedFiles.value.length !== 1) return '';
    const file = files.value.find(f => f.id === selectedFiles.value[0]);
    return file?.type || '';
});
const previewLoading = ref(false);
const previewError = ref(false);

const selectedFilePreview = computed(() => {
    if (selectedFiles.value.length !== 1) return '';
    const file = files.value.find(f => f.id === selectedFiles.value[0]);
    
    // 演示模式 - 返回模拟预览
    if (import.meta.env.MODE === 'development') {
        switch(file.type) {
            case 'image':
                return '/src/assets/images/logo.png';
            case 'pdf':
                return '/src/assets/images/data-manage.png';
            case 'video':
                return '/src/assets/images/home-banner.png';
            default:
                return '';
        }
    }

    /* 正式API调用代码 (保留但暂时注释)
    try {
        previewLoading.value = true;
        previewError.value = false;
        const response = await apiService.getFilePreview({
            fileId: file.id,
            type: file.type
        });
        if (response.success) {
            return response.data.url;
        }
        previewError.value = true;
        return '';
    } catch (error) {
        previewError.value = true;
        return '';
    } finally {
        previewLoading.value = false;
    }
    */
    return '';
});
const selectedFilePath = computed(() => {
    if (selectedFiles.value.length !== 1) return '';
    const pathStr = currentPath.value.join('/');
    return pathStr ? `/${pathStr}/` : '/';
});
const getFileIcon = (type: string) => {
    const iconMap: Record<string, string> = {
        // 办公文档
        doc: 'fas fa-file-word',
        xls: 'fas fa-file-excel',
        ppt: 'fas fa-file-powerpoint',
        // PDF
        pdf: 'fas fa-file-pdf',
        // 图片
        image: 'fas fa-file-image',
        // 视频
        video: 'fas fa-file-video',
        // 音频
        audio: 'fas fa-file-audio',
        // 压缩文件
        archive: 'fas fa-file-archive',
        // 代码文件
        code: 'fas fa-file-code',
        // 设计文件
        psd: 'fas fa-file-image',
        ai: 'fas fa-file-image',
        // 配置文件
        config: 'fas fa-file-alt',
        // 文件夹
        folder: 'fas fa-folder'
    };
    return iconMap[type] || 'fas fa-file';
};
const getFileColor = (type: string) => {
    const colorMap: Record<string, string> = {
        // 办公文档
        doc: '#4285f4',
        xls: '#0f9d58', 
        ppt: '#ff5722',
        // PDF
        pdf: '#ff4444',
        // 图片
        image: '#42b883',
        // 视频
        video: '#fb8c00',
        // 音频
        audio: '#9c27b0',
        // 压缩文件
        archive: '#795548',
        // 代码文件
        code: '#673ab7',
        // 设计文件
        psd: '#607d8b',
        ai: '#607d8b',
        // 配置文件
        config: '#9e9e9e'
    };
    return colorMap[type] || '#757575';
};
const toggleFileSelection = (fileId: number) => {
    const index = selectedFiles.value.indexOf(fileId);
    if (index === -1) {
        selectedFiles.value = [fileId];
    } else {
        selectedFiles.value.splice(index, 1);
    }
};
const showContextMenu = (event: MouseEvent, file: any) => {
    event.preventDefault();
    menuPosition.value = {
        x: event.clientX,
        y: event.clientY
    };
    showMenu.value = true;
    if (!selectedFiles.value.includes(file.id)) {
        selectedFiles.value = [file.id];
    }
};
const navigateTo = (index: number) => {
    currentPath.value = currentPath.value.slice(0, index + 1);
};

const handleFileDoubleClick = (file: any) => {
    if (file.type === 'folder') {
        currentPath.value = [...currentPath.value, file.name];
        selectedFiles.value = [];
    }
};
// 点击其他地方关闭右键菜单
const handleUploadSuccess = () => {
  refreshFileList();
  showUploadModal.value = false;
};

const handleCreateFolderSuccess = () => {
  refreshFileList();
  showCreateFolderModal.value = false;
};

const refreshFileList = async () => {
  try {
    const response = await apiService.getFileList({
      path: currentPath.value.join('/')
    });
    if (response.success) {
      files.value = response.data;
    }
  } catch (error) {
    console.error('获取文件列表失败:', error);
  }
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const closeContextMenu = (event: MouseEvent) => {
    if (showMenu.value) {
        showMenu.value = false;
    }
};
onUnmounted(() => {
    window.removeEventListener('click', closeContextMenu);
});
window.addEventListener('click', closeContextMenu);
</script>
<style scoped></style>
