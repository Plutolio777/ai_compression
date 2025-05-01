<template>
  <!-- 模态框遮罩 -->
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <!-- 主容器 -->
    <div class="bg-white rounded-2xl shadow-lg w-full max-w-md overflow-hidden transition-all duration-300
                border border-gray-100 hover:shadow-xl"
         style="background-image: radial-gradient(circle at 100% 0%, rgba(229, 247, 255, 0.3) 0%, transparent 40%),
                radial-gradient(circle at 0% 100%, rgba(203, 237, 255, 0.3) 0%, transparent 40%)">
      <!-- 标题栏 -->
      <div class="bg-white p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-800 relative">
          {{ isLogin ? '用户登录' : '用户注册' }}
        </h2>
        <button @click="visible = false" class="text-gray-400 hover:text-gray-600">
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>
      
      <!-- 登录表单 -->
      <div v-if="isLogin" class="p-6 space-y-4">
        <div class="space-y-2">
          <label class="block text-gray-700">账号</label>
          <input v-model="loginForm.username" 
                 class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                 placeholder="请输入用户名"
                 autocomplete="off"
                 readonly
                 onfocus="this.removeAttribute('readonly')">
          <div v-if="loginErrors.username" class="text-red-500 text-sm">{{ loginErrors.username }}</div>
        </div>

        <div class="space-y-2">
          <label class="block text-gray-700">密码</label>
            <input v-model="loginForm.password" type="password" autocomplete="new-password"
                   class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                   placeholder="请输入密码">
          <div v-if="loginErrors.password" class="text-red-500 text-sm">{{ loginErrors.password }}</div>
        </div>

        <button @click="handleLogin" 
                class="w-full px-6 py-3 bg-white text-blue-600 rounded-xl border border-blue-200
                       hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200
                       shadow-none hover:shadow-sm">
          登录
        </button>

        <div class="text-center mt-4">
          <span class="text-gray-600">没有账号？</span>
          <button @click="toggleForm" class="text-blue-600 hover:underline">立即注册</button>
        </div>
      </div>

      <!-- 注册表单 -->
      <div v-else class="p-6 space-y-4">
        <div class="flex justify-center">
          <div class="relative">
            <input type="file" ref="avatarInput" @change="handleAvatarChange" 
                   class="hidden" accept="image/*">
            <div @click="$refs.avatarInput.click()" 
                 class="w-24 h-24 rounded-full bg-gray-100 flex items-center justify-center 
                        cursor-pointer overflow-hidden border-2 border-dashed border-gray-300 hover:border-blue-500">
              <img v-if="registerForm.avatarUrl" :src="registerForm.avatarUrl" 
                   class="w-full h-full object-cover">
              <div v-else class="text-gray-400">
                <i class="fas fa-user-plus text-2xl"></i>
              </div>
            </div>
            <div v-if="registerErrors.avatar" class="text-red-500 text-sm text-center mt-2">
              {{ registerErrors.avatar }}
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div class="space-y-2">
            <label class="block text-gray-700">用户名</label>
            <input v-model="registerForm.name"
                   class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                   placeholder="请输入用户名"
                   autocomplete="off"
                   readonly
                   onfocus="this.removeAttribute('readonly')">
            <div v-if="registerErrors.name" class="text-red-500 text-sm">{{ registerErrors.name }}</div>
          </div>

          <div class="space-y-2">
            <label class="block text-gray-700">手机号</label>
            <input v-model="registerForm.mobile"
                   class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                   placeholder="请输入手机号"
                   autocomplete="off"
                   readonly
                   onfocus="this.removeAttribute('readonly')">
            <div v-if="registerErrors.mobile" class="text-red-500 text-sm">{{ registerErrors.mobile }}</div>
          </div>

          <div class="space-y-2">
            <label class="block text-gray-700">邮箱</label>
            <input v-model="registerForm.email"
                   class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                   placeholder="请输入邮箱"
                   autocomplete="off"
                   readonly
                   onfocus="this.removeAttribute('readonly')">
            <div v-if="registerErrors.email" class="text-red-500 text-sm">{{ registerErrors.email }}</div>
          </div>

          <div class="space-y-2">
            <label class="block text-gray-700">密码</label>
            <input v-model="registerForm.password" type="password" autocomplete="new-password"
                   class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                   placeholder="请输入密码">
            <div v-if="registerErrors.password" class="text-red-500 text-sm">{{ registerErrors.password }}</div>
          </div>

          <button @click="handleRegister" 
                  class="w-full px-6 py-3 bg-white text-blue-600 rounded-xl border border-blue-200
                         hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200
                         shadow-none hover:shadow-sm">
            注册
          </button>

          <div class="text-center mt-4">
            <span class="text-gray-600">已有账号？</span>
            <button @click="toggleForm" class="text-blue-600 hover:underline">直接登录</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import apiService from '@/api/apiService'
import { useStore } from 'vuex'

const store = useStore()
const visible = ref(false)
const isLogin = ref(true)
const avatarInput = ref(null)

const loginForm = ref({
  username: '',
  password: ''
})

const loginErrors = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  name: '',
  mobile: '',
  email: '',
  password: '',
  avatar: null,
  avatarUrl: ''
})

const registerErrors = ref({
  name: '',
  mobile: '',
  email: '',
  password: '',
  avatar: ''
})

const toggleForm = () => {
  isLogin.value = !isLogin.value
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (!file) return

  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    registerErrors.value.avatar = '只能上传图片文件!'
    return
  }
  if (!isLt2M) {
    registerErrors.value.avatar = '图片大小不能超过2MB!'
    return
  }

  registerForm.value.avatar = file
  registerForm.value.avatarUrl = URL.createObjectURL(file)
  registerErrors.value.avatar = ''
}

const validateLogin = () => {
  let valid = true
  loginErrors.value = { username: '', password: '' }

  if (!loginForm.value.username) {
    loginErrors.value.username = '请输入用户名'
    valid = false
  }

  if (!loginForm.value.password) {
    loginErrors.value.password = '请输入密码'
    valid = false
  } else if (loginForm.value.password.length < 6) {
    loginErrors.value.password = '密码长度不能少于6位'
    valid = false
  }

  return valid
}

const validateRegister = () => {
  let valid = true
  registerErrors.value = { name: '', mobile: '', email: '', password: '', avatar: '' }

  if (!registerForm.value.name) {
    registerErrors.value.name = '请输入用户名'
    valid = false
  }

  if (!registerForm.value.mobile) {
    registerErrors.value.mobile = '请输入手机号'
    valid = false
  } else if (!/^1[3-9]\d{9}$/.test(registerForm.value.mobile)) {
    registerErrors.value.mobile = '手机号格式不正确'
    valid = false
  }

  if (!registerForm.value.email) {
    registerErrors.value.email = '请输入邮箱'
    valid = false
  } else if (!/^\S+@\S+\.\S+$/.test(registerForm.value.email)) {
    registerErrors.value.email = '邮箱格式不正确'
    valid = false
  }

  if (!registerForm.value.password) {
    registerErrors.value.password = '请输入密码'
    valid = false
  } else if (registerForm.value.password.length < 6) {
    registerErrors.value.password = '密码长度不能少于6位'
    valid = false
  }

  if (!registerForm.value.avatar && !registerForm.value.avatarUrl) {
    registerErrors.value.avatar = '请上传头像'
    valid = false
  }

  return valid
}

const showMessage = (type, message) => {
  const messageEl = document.createElement('div')
  messageEl.className = `fixed top-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-md shadow-md z-50 ${
    type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
  }`
  messageEl.textContent = message
  document.body.appendChild(messageEl)

  setTimeout(() => {
    messageEl.classList.add('opacity-0', 'transition-opacity', 'duration-300')
    setTimeout(() => messageEl.remove(), 300)
  }, 3000)
}

const handleLogin = async () => {
  if (!validateLogin()) return

  try {
    const res = await apiService.login(
      { username: loginForm.value.username, password: loginForm.value.password },
      {}, // params
      {}, // pathParams
      {}, // headers
      { requiresAuth: false }
    )
    if (res.success) {
      // 处理注册成功响应
      const userData = res.data.user || res.data;
      store.commit('setUser', {
        user: userData,
        token: userData.token?.access || '',
        refreshToken: userData.token?.refresh || ''
      });
      visible.value = false
      showMessage('success', '登录成功')
    } else {
      showMessage('error', res.error || '登录失败')
    }
  } catch (error) {
    showMessage('error', '登录请求失败')
  }
}

const handleRegister = async () => {
  if (!validateRegister()) return

  try {
    const res = await apiService.register(
      {
        username: registerForm.value.name,
        name: registerForm.value.name,
        mobile: registerForm.value.mobile,
        email: registerForm.value.email,
        password: registerForm.value.password,
        avatar: registerForm.value.avatar
      },
      {}, // params
      {}, // pathParams
      {}, // headers
      { isFileUpload: true, fileKey: 'avatar', requiresAuth: false }
    )
    if (res.success) {
      // 处理注册成功响应
      const userData = res.data.user || res.data;
      store.commit('setUser', {
        user: userData,
        token: userData.token?.access || res.data.token?.access || '',
        refreshToken: userData.token?.refresh || res.data.token?.refresh || ''
      });
      isLogin.value = true
      showMessage('success', '注册成功')
    } else {
      showMessage('error', res.error || '注册失败')
    }
  } catch (error) {
    showMessage('error', '注册请求失败')
  }
}

defineExpose({
  show: () => {
    visible.value = true
    isLogin.value = true
  }
})
</script>

<style>
/* 移除浏览器默认输入框样式 */
input {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  outline: none;
}

/* 禁用浏览器自动填充样式 */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px white inset !important;
  -webkit-text-fill-color: #333 !important;
  transition: background-color 5000s ease-in-out 0s;
}

/* 自定义输入框聚焦样式 */
input:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* 移除文件输入框默认样式 */
input[type="file"] {
  display: none;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
