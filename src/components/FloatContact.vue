<template>
  <div class="fixed right-6 bottom-6 z-50">
    <div class="flex flex-col items-end space-y-3">
      <!-- 客服按钮 -->
      <button @click="showContact = !showContact" 
              class="w-14 h-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all flex items-center justify-center">
        <i class="fas fa-headset text-2xl"></i>
      </button>

      <!-- 联系表单 -->
      <transition name="fade">
        <div v-if="showContact" class="bg-white rounded-lg shadow-xl w-80 p-4">
          <h3 class="text-lg font-bold mb-3">联系我们</h3>
          <form @submit.prevent="submitForm" class="space-y-3">
            <input v-model="form.name" 
                   placeholder="您的姓名" 
                   class="w-full px-3 py-2 border rounded-lg">
            <input v-model="form.phone" 
                   placeholder="联系电话" 
                   class="w-full px-3 py-2 border rounded-lg">
            <textarea v-model="form.message" 
                      placeholder="咨询内容" 
                      rows="3"
                      class="w-full px-3 py-2 border rounded-lg"></textarea>
            <button type="submit" 
                    class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
              提交咨询
            </button>
          </form>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showContact = ref(false)
const form = ref({
  name: '',
  phone: '', 
  message: ''
})

const submitForm = () => {
  // TODO: 对接API提交表单
  alert('咨询已提交，我们将尽快联系您！')
  showContact.value = false
  form.value = { name: '', phone: '', message: '' }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
