<!-- 代码已包含 CSS：使用 TailwindCSS , 安装 TailwindCSS 后方可看到布局样式效果 -->
<template>
    <div class="min-h-screen bg-gray-50">
        <!-- 顶部导航 -->
        <nav class="fixed top-0 w-full h-16 bg-white shadow-sm z-50">
            <div class="w-full px-6 h-full flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <i class="fas fa-cube text-blue-500 text-2xl"></i>
                    <span class="text-xl font-medium">智能压缩系统</span>
                </div>
                <div class="flex items-center space-x-6">
                    <button
                        class="!rounded-button whitespace-nowrap flex items-center space-x-1 text-gray-600 hover:text-blue-500">
                        <i class="fas fa-bell"></i>
                        <span>通知</span>
                    </button>
                    <button
                        class="!rounded-button whitespace-nowrap flex items-center space-x-1 text-gray-600 hover:text-blue-500">
                        <i class="fas fa-cog"></i>
                        <span>设置</span>
                    </button>
                    <div class="relative" @click.stop="toggleUserMenu">
                      <div class="flex items-center space-x-2 cursor-pointer">
                        <div class="w-8 h-8 rounded-full overflow-hidden">
                          <img :src="user?.avatar || avatarUrl" class="w-full h-full object-cover" alt="用户头像" />
                        </div>
                        <span class="text-gray-700">{{ user?.name || '未登录' }}</span>
                      </div>
                      <transition name="fade">
                        <div v-if="showUserMenu" class="absolute right-0 mt-2 w-64 bg-white shadow-lg rounded-lg p-4 z-50">
                          <div v-if="user" class="space-y-3">
                            <div class="flex items-center space-x-3">
                              <img :src="user.avatar || avatarUrl" class="w-12 h-12 rounded-full">
                              <div>
                                <p class="font-medium">{{ user.name }}</p>
                                <p class="text-sm text-gray-500">{{ user.email }}</p>
                              </div>
                            </div>
                            <div class="text-sm"><span class="text-gray-500">公司：</span>{{ user.company || '未设置' }}</div>
                            <div class="text-sm"><span class="text-gray-500">职位：</span>{{ user.position || '未设置' }}</div>
                            <button @click="logout" class="w-full mt-2 text-red-500 hover:bg-red-50 p-2 rounded text-sm">
                              退出登录
                            </button>
                          </div>
                          <div v-else class="space-y-2">
                            <button @click="openLoginModal" class="w-full bg-blue-500 text-white p-2 rounded">
                              登录/注册
                            </button>
                          </div>
                        </div>
                      </transition>
                    </div>
                </div>
            </div>
        </nav>
        <!-- 主体内容 -->
        <div v-if="!user" class="pt-16 flex min-h-screen bg-gray-50">
          <HomePage></HomePage>
        </div>
        <div v-else class="pt-16 flex min-h-screen bg-gray-50">
            <!-- 左侧菜单 -->
            <div class="w-64 bg-white shadow-sm fixed left-0 top-16 bottom-0 overflow-y-auto">
                <div class="p-4 space-y-2">
                    <button v-for="(item, index) in menuItems" :key="index" :class="[
                        'w-full text-left px-4 py-3 rounded-lg flex items-center space-x-3 !rounded-button whitespace-nowrap',
                        currentMenu === item.id ? 'bg-blue-50 text-blue-500' : 'text-gray-600 hover:bg-gray-50'
                    ]" @click="currentMenu = item.id">
                        <i :class="item.icon"></i>
                        <span>{{ item.name }}</span>
                    </button>
                </div>
            </div>
            <!-- 右侧内容区 -->
            <!-- 智能解压缩内容 -->
            <div v-if="currentMenu === 'compress'" class="flex-1 ml-64 p-6">
                <Compression/>
            </div>
            <!-- 网盘中心内容 -->
            <div v-if="currentMenu === 'cloud'" class="flex-1 ml-64 min-h-screen">
                <Files/>
            </div>
            <!-- 模型配置内容 -->
            <div v-if="currentMenu === 'model'" class="flex-1 ml-64 p-6">
                <ModelConfig/>
            </div>
            <!-- 智能策略内容 -->
            <div v-if="currentMenu === 'strategy'" class="flex-1 ml-64 p-6">
                <Strategy/>
            </div>
            <!-- 标签管理内容 -->
            <div v-if="currentMenu === 'tags'" class="flex-1 ml-64 p-6">
                <Tags/>
            </div>
        </div>
    </div>



</template>
<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import Compression from './views/Compression.vue';
import Files from './views/Files.vue';
import ModelConfig from './views/ModelConfig.vue';
import Strategy from './views/Strategy.vue';
import Tags from './views/Tags.vue';
import HomePage from './views/HomePage.vue';

const avatarUrl = 'https://ai-public.mastergo.com/ai/img_res/9099b9d9c052e912f4fb1f438e5b117b.jpg';

const store = useStore();
const currentMenu = ref('compress');
const showUserMenu = ref(false);
const user = computed(() => store.state.user);

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

const logout = () => {
  store.commit('clearUser');
  showUserMenu.value = false;
  // 这里可以添加跳转到首页的逻辑
};

const openLoginModal = () => {
  showUserMenu.value = false;
  // 这里可以触发登录弹窗显示
};
const menuItems = [
    { id: 'compress', name: '智能解压缩', icon: 'fas fa-compress-arrows-alt' },
    { id: 'cloud', name: '网盘中心', icon: 'fas fa-cloud' },
    { id: 'model', name: '模型配置', icon: 'fas fa-sliders-h' },
    { id: 'strategy', name: '智能策略', icon: 'fas fa-brain' },
    { id: 'tags', name: '标签管理', icon: 'fas fa-tags' },
    { id: 'settings', name: '系统设置', icon: 'fas fa-cog' },
];



// 点击外部关闭弹窗
const handleClickOutside = (event) => {
  const userMenu = event.target.closest('.relative');
  if (!userMenu && showUserMenu.value) {
    showUserMenu.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// 初始化时设置当前菜单为网盘中心
currentMenu.value = 'cloud';

</script>
<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
</style>
