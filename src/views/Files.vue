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
                <button class="hover:text-blue-500" @click="resetToRoot">
                    <i class="fas fa-home"></i>
                </button>
                <button v-if="currentPath.length > 0"
                    class="hover:text-blue-500 ml-2" 
                    @click="returnToLastLevel">
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
                <template v-if="files.length > 0">
                    <div v-for="file in files" :key="file.id"
                        class="relative group bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                        :class="{ 'ring-2 ring-blue-500': selectedFiles.includes(file.id) }"
                        @click="toggleFileSelection(file.id)" 
                        @dblclick="handleFileDoubleClick(file)"
                        @contextmenu.prevent="showContextMenu($event, file)">
                        <div class="flex flex-col items-center h-full">
                            <div class="w-16 h-16 mb-2 flex items-center justify-center">
                                <i :class="getFileIcon(file.name)" class="text-4xl"
                                    :style="{ color: getFileColor(file.name) }"></i>
                            </div>
                            <p class="text-sm text-center font-medium truncate w-full">{{ file.name }}</p>
                            <p class="text-xs text-gray-500">{{ file.size }}</p>
                            <!-- 标签区域 -->
                            <div class="absolute top-2 right-2 grid grid-auto-flow-row gap-y-1 justify-items-end">
                                <template v-for="tag in file.tags" :key="tag.id">
                                    <div 
                                        class="flex items-center px-1.5 py-0.5 text-xs rounded truncate w-fit max-w-[48px]"
                                        :style="{
                                            backgroundColor: getTagColor(tag.importance) + '20',
                                            color: getTagColor(tag.importance)
                                        }"
                                        :title="tag.name"
                                    >
                                        <span class="truncate">{{ tag.name }}</span>
                                        <button 
                                            v-if="selectedFiles.includes(file.id)"
                                            @click.stop="removeTag(file.id, tag.id)"
                                            class="ml-1 text-gray-500 hover:text-red-500"
                                        >
                                            <i class="fas fa-times text-xs"></i>
                                        </button>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </template>
                <div v-else class="col-span-6 py-16 text-center">
                    <i class="fas fa-folder-open text-4xl text-gray-300 mb-4"></i>
                    <p class="text-gray-500">暂无数据</p>
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
                    <template v-if="files.length > 0">
                        <div v-for="file in files" :key="file.id"
                            class="grid grid-cols-12 gap-4 p-4 hover:bg-gray-50 cursor-pointer items-center"
                            :class="{ 'bg-blue-50': selectedFiles.includes(file.id) }" 
                            @click="toggleFileSelection(file.id)"
                            @dblclick="handleFileDoubleClick(file)"
                            @contextmenu.prevent="showContextMenu($event, file)">
                            <div class="col-span-6 flex items-center space-x-3">
                                <i :class="getFileIcon(file.name)" :style="{ color: getFileColor(file.name) }"></i>
                                <span>{{ file.name }}</span>
                            </div>
                            <div class="col-span-2 text-gray-500">{{ file.size }}</div>
                            <div class="col-span-2 text-gray-500">{{ file.modifiedTime }}</div>
                            <div class="col-span-2 flex flex-wrap gap-1 min-w-[120px]">
                                <div class="group relative inline-block">
                                    <div class="flex flex-wrap gap-1 items-center">
                                <template v-for="(tag, index) in file.tags.slice(0, 3)" :key="tag.id">
                                    <span 
                                        class="px-2 py-1 text-xs rounded flex items-center whitespace-nowrap"
                                        :style="{
                                            backgroundColor: getTagColor(tag.importance) + '20', 
                                            color: getTagColor(tag.importance),
                                            border: `1px solid ${getTagColor(tag.importance)}`
                                        }"
                                    >
                                        {{ tag.name }}
                                        <button 
                                            v-if="selectedFiles.includes(file.id)"
                                            @click.stop="removeTag(file.id, tag.id)"
                                            class="ml-1 text-gray-500 hover:text-red-500"
                                        >
                                            <i class="fas fa-times text-xs"></i>
                                        </button>
                                    </span>
                                </template>
                                <span 
                                    class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                                >
                                    +{{ file.tags.length - 3 }}
                                </span>
                                    </div>
                                    <div 
                                        v-if="file.tags.length > 0"
                                        class="absolute z-10 hidden group-hover:block bg-white shadow-lg rounded-md p-2 mt-1 min-w-max"
                                    >
                                        <div class="flex flex-wrap gap-1">
                                            <template v-for="tag in file.tags" :key="tag.id">
                                                <span 
                                                    class="px-2 py-1 text-xs rounded"
                                                    :style="{
                                                        backgroundColor: getTagColor(tag.importance) + '20', 
                                                        color: getTagColor(tag.importance)
                                                    }"
                                                >
                                                    {{ tag.name }}
                                                    <button 
                                                        v-if="selectedFiles.includes(file.id)"
                                                        @click.stop="removeTag(file.id, tag.id)"
                                                        class="ml-1 text-gray-500 hover:text-red-500"
                                                    >
                                                        <i class="fas fa-times text-xs"></i>
                                                    </button>
                                                </span>
                                            </template>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                    <div v-else class="py-16 text-center">
                        <i class="fas fa-folder-open text-4xl text-gray-300 mb-4"></i>
                        <p class="text-gray-500">暂无数据</p>
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
        <button 
          class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm"
          @click.stop="handleAddTagClick"
        >
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
      :parent-id="idStack.length > 0 ? idStack[idStack.length - 1] : null"
      @close="showCreateFolderModal = false"
      @create-success="handleCreateFolderSuccess"
    />

    <!-- 标签管理浮动弹窗 -->
    <div v-if="showTagModal" class="fixed bg-white shadow-lg rounded-lg z-50"
        :style="{
          top: `${menuPosition.y + 20}px`,
          left: `${menuPosition.x}px`
        }"
        @click.stop>
      <TagSelector
        :file-id="currentTagFile.id"
        @close="showTagModal = false"
        @refresh="fetchFiles"
      />
    </div>
</template>
<script lang="ts" setup>
console.log(111111111111111111)
import { ref, onMounted, onUnmounted, reactive, computed, nextTick } from 'vue';
import UploadModal from '../components/UploadModal.vue';
import CreateFolderModal from '../components/CreateFolderModal.vue';
import TagSelector from '../components/TagSelector.vue';
import apiService from '../api/apiService';
import { iconMap, colorMap } from '../assets/fileTypes';

const showUploadModal = ref(false);
const showCreateFolderModal = ref(false);
const showTagModal = ref(false);
const currentTagFile = ref(null);

// 打开标签管理弹窗
const openTagModal = (file) => {
  console.log('打开标签弹窗，文件:', file);
  currentTagFile.value = file;
  showTagModal.value = true;
};


// 网盘功能相关数据
const viewMode = ref<'grid' | 'list'>('grid');
const searchQuery = ref('');
// 使用更可靠的ref初始化方式
const currentPath = ref([])
console.log(currentPath.value.length)
const idStack = ref([])
// 确保初始化时加载根目录

const selectedFiles = ref<number[]>([]);
const showMenu = ref(false);
const menuPosition = ref({ x: 0, y: 0 });
const files = ref([]);

// 获取文件列表
const fetchFiles = async () => {
    try {
        let queryParams = {};
        if (idStack.value.length > 0) {
            queryParams.parent_id = idStack.value[idStack.value.length - 1];
        }
        if (searchQuery.value) {
            queryParams.search_query = searchQuery.value;
        }
        
        const response = await apiService.getFileTree(
            {}, // 请求体数据
            queryParams // 查询参数
        );
    if (response.success) {
        console.log('获取到的文件数据:', response.data);
        files.value = Array.isArray(response.data) ? response.data : [];
        console.log('currentPath:', currentPath.value);
        console.log('files:', files.value);
    }
    } catch (error) {
    console.error('获取文件列表失败:', error);
    }
};

// 初始化加载文件列表
onMounted(() => {
  fetchFiles();
});
const returnToLastLevel = () => {
    currentPath.value = currentPath.value.slice(0, -1);
    idStack.value = idStack.value.slice(0, -1);
    selectedFiles.value = [];
    fetchFiles();
}
const getCurrentLevelFiles = () => {
    console.log('getCurrentLevelFiles - currentPath:', currentPath.value);
    console.log('getCurrentLevelFiles - files:', files.value);
    
    if (!Array.isArray(files.value)) return [];
    
    let currentFiles = [...files.value];
    
    for (const folderName of currentPath.value) {
        const folder = currentFiles.find(f => 
            f.type === 'folder' && 
            f.name === folderName && 
            Array.isArray(f.children)
        );
        
        if (!folder) {
            console.warn(`找不到文件夹: ${folderName}`);
            return [];
        }
        
        currentFiles = [...folder.children];
        console.log(`进入文件夹 ${folderName} 后的文件列表:`, currentFiles);
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

    return '';
});
const selectedFilePath = computed(() => {
    if (selectedFiles.value.length !== 1) return '';
    const pathStr = currentPath.value.join('/');
    return pathStr ? `/${pathStr}/` : '/';
});
const getFileExtension = (filename: string) => {
    if (filename === 'folder') return 'folder';
    const parts = filename.split('.');
    return parts.length > 1 ? parts.pop()?.toLowerCase() || 'file' : 'file';
};

const getFileIcon = (filename: string) => {
    const type = getFileExtension(filename);
    return iconMap[type] || 'fas fa-file';
};
const getFileColor = (filename: string) => {
    const type = getFileExtension(filename);
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
const contextMenuFile = ref(null);

const showContextMenu = (event: MouseEvent, file: any) => {
    event.preventDefault();
    console.log('显示右键菜单，文件:', file);
    contextMenuFile.value = file;
    menuPosition.value = {
        x: event.clientX,
        y: event.clientY
    };
    showMenu.value = true;
    if (!selectedFiles.value.includes(file.id)) {
        selectedFiles.value = [file.id];
    }
    console.log('当前选中文件:', selectedFiles.value);
};
const navigateTo = (index: number) => {
    currentPath.value = currentPath.value.slice(0, index + 1);
    idStack.value = idStack.value.slice(0, index + 1);
    selectedFiles.value = [];
    fetchFiles(); // 路径切换时刷新文件列表
};

const handleFileDoubleClick = async (file: any) => {
    if (file.type === 'folder') {
        console.log('双击文件夹:', file.name);
        currentPath.value = [...currentPath.value, file.name];
        idStack.value = [...idStack.value, file.id];
        selectedFiles.value = [];
        console.log('currentPath更新为:', currentPath.value);
        await fetchFiles(); // 确保先完成文件加载
        console.log('currentPath after update:', currentPath.value);
    }
};

// 点击其他地方关闭右键菜单
const handleUploadSuccess = () => {
  fetchFiles(); // 使用fetchFiles而不是refreshFileList保持一致性
  showUploadModal.value = false;
};

const handleCreateFolderSuccess = () => {
  fetchFiles(); // 使用fetchFiles而不是refreshFileList保持一致性
  showCreateFolderModal.value = false;
};

// 处理标签更新
const handleRemoveTag = async (fileId, tagId) => {
  try {
    const response = await apiService.removeFileTag(
      { tag_id: tagId },
      {},
      { id: fileId }
    );
    if (response.success) {
      // 更新本地标签数据
      if (fileTags.value[fileId]) {
        fileTags.value[fileId] = fileTags.value[fileId].filter(tag => tag.id !== tagId);
      }
      // 更新文件列表中的标签显示
      const fileIndex = files.value.findIndex(f => f.id === fileId);
      if (fileIndex !== -1) {
        files.value[fileIndex].tags = files.value[fileIndex].tags.filter(tag => tag.id !== tagId);
      }
    }
  } catch (error) {
    console.error('删除标签失败:', error);
  }
};

const handleUpdateTags = async (tags) => {
  try {
    const response = await apiService.updateFileTags(
      { tags },
      {},
      { id: currentTagFile.value.id }
    );
    if (response.success) {
      fileTags.value[currentTagFile.value.id] = tags;
      // 更新文件列表中的标签显示
      const fileIndex = files.value.findIndex(f => f.id === currentTagFile.value.id);
      if (fileIndex !== -1) {
        files.value[fileIndex].tags = tags;
      }
    }
  } catch (error) {
    console.error('更新文件标签失败:', error);
  }
  showTagModal.value = false;
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

const resetToRoot = () => {
  currentPath.value = [];
  idStack.value = [];
  selectedFiles.value = [];
  setTimeout(fetchFiles, 0);
};

const getTagColor = (importance) => {
  // 根据重要性返回不同颜色
  return importance === 1 ? '#4CAF50' :  // 低 - 绿色
         importance === 2 ? '#FFC107' :  // 中 - 黄色
         '#F44336';                      // 高 - 红色
};

const removeTag = async (fileId, tagId) => {
  try {
    const response = await apiService.removeFileTag(
      { tag_id: tagId },
      {},
      { id: fileId }
    );
    if (response.success) {
      // 更新本地文件标签数据
      const fileIndex = files.value.findIndex(f => f.id === fileId);
      if (fileIndex !== -1) {
        files.value[fileIndex].tags = files.value[fileIndex].tags.filter(
          tag => tag.id !== tagId
        );
      }
      showToast('标签删除成功');
    } else {
      showToast(response.error || '删除标签失败', 'error');
    }
  } catch (error) {
    showToast('删除标签出错: ' + error.message, 'error');
  }
};

const handleAddTagClick = (e) => {
  e.stopPropagation();
  console.log('点击添加标签，当前文件:', contextMenuFile.value);
  if (contextMenuFile.value) {
    openTagModal(contextMenuFile.value);
    showMenu.value = false; // 关闭右键菜单
  }
};

const showToast = (message: string, type: 'success' | 'error' = 'success') => {
  const toast = document.createElement('div');
  toast.className = `fixed top-4 right-4 px-4 py-2 rounded-md shadow-lg text-white ${
    type === 'success' ? 'bg-green-500' : 'bg-red-500'
  }`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
};

const closeContextMenu = (event: MouseEvent) => {
  // 不关闭右键菜单如果点击的是标签弹窗
  const isTagModalClick = event.composedPath().some(el => 
    el.classList && el.classList.contains('tag-selector-modal')
  );
  if (showMenu.value && !isTagModalClick) {
    showMenu.value = false;
  }
};
onUnmounted(() => {
    window.removeEventListener('click', closeContextMenu);
});
window.addEventListener('click', closeContextMenu);
console.log(currentPath.value.length)
</script>
<style scoped></style>
