import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import 'element-plus/dist/index.css'
import ElementUI from "element-plus"
import router from './router'
import '@fortawesome/fontawesome-free/css/all.min.css';
import './assets/index.css'
import store from './store';

const app = createApp(App)
// app.config.globalProperties.$apiService = apiService;
app.use(ElementUI)
app.use(router)
app.use(store);
app.mount('#app')
