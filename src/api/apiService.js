import axios from 'axios';
import store from '@/store'; // 引入 Vuex store

// 创建 axios 实例
const instance = axios.create({
    timeout: 10000, // 设置请求超时时间
});

// 获取当前登录的用户信息
function getAccess() {
    // Try localStorage first, then Vuex store
    return localStorage.getItem('access') || store.state.accessToken;
}

function getRefresh() {
    // Try localStorage first, then Vuex store
    return localStorage.getItem('refresh') || store.state.refreshToken;
}


// 添加请求拦截器，判断用户是否登录
instance.interceptors.request.use(
    async (config) => {
        if (config.requiresAuth) {
            const access = getAccess();
            if (access) {
                config.headers['Authorization'] = `Bearer ${access}`;
            } else {
                // 尝试刷新token
                const refreshToken = getRefresh();
                if (refreshToken) {
                    try {
                const res = await axios({
                    method: 'POST',
                    url: '/api/auth/refresh/',
                    data: { refresh: refreshToken }
                });
                if (res.data && res.data.access) {
                    const { access } = res.data;
                    store.commit('setUser', {
                        user: store.state.user,
                        token: access,
                        refreshToken: refreshToken // Keep same refresh token
                    });
                            config.headers['Authorization'] = `Bearer ${access}`;
                            return config;
                        }
                    } catch (error) {
                        console.error('刷新token失败:', error);
                    }
                }
                console.error('用户未登录，请先登录');
                return Promise.reject(new Error('用户未登录'));
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 处理文件上传和其他数据
function handleFileUpload(data, isFileUpload, fileKey) {
    if (!isFileUpload) return data; // 如果不需要上传文件，直接返回原数据

    const formData = new FormData();

    // 如果 isFileUpload 为 true，处理文件上传
    if (Array.isArray(data[fileKey])) {
        // 如果文件是数组，逐个添加文件，添加索引
        data[fileKey].forEach((file, index) => {
            formData.append(`${fileKey}[${index}]`, file); // 给每个文件添加索引
        });
    } else {
        // 如果是单个文件，直接添加
        formData.append(fileKey, data[fileKey]);
    }

    // 添加其他非文件字段
    Object.keys(data).forEach((key) => {
        if (key !== fileKey) {
            formData.append(key, data[key]);
        }
    });

    return formData; // 返回处理后的 FormData
}

// 统一的请求方法，处理所有不同的请求
// 统一的请求方法，处理所有不同的请求
async function request({method, url, data, params, pathParams, headers, isFileUpload, fileKey, requiresAuth, ...config}) {
    // 替换路径参数
    if (pathParams) {
        Object.keys(pathParams).forEach((key) => {
            url = url.replace(`:${key}`, pathParams[key]);
        });
    }

    // 如果需要文件上传，根据 isFileUpload 和 FileKey 处理数据
    if (isFileUpload) {
        data = handleFileUpload(data, isFileUpload, fileKey);
        headers = {...headers, 'Content-Type': 'multipart/form-data'};
    } else {
        // 如果没有文件，使用 JSON 格式
        headers = {...headers, 'Content-Type': 'application/json'};
        data = JSON.stringify(data);
    }

    // 设置请求配置
    const axiosConfig = {
        method,
        url,
        headers: {...headers},
        params,  // GET 请求参数
        data,    // POST 请求体数据
        requiresAuth,
        ...config
    };

    // return await instance(config);
    try {
        // 发起请求
        const response = await instance(axiosConfig);
        // console.log(123, response);
        // 可以根据需求对返回的数据进行处理（例如统一格式化）
        if (200 <= response.status && response.status < 300) {
            // 假设所有响应都包含一个 `data` 字段
            return {
                success: true,
                data: response.data,
            };
        } else if (response.status === 201) {
            // 处理201 Created响应
            return {
                success: true,
                data: response.data,
            };
        } else {
            // 如果返回的状态码不是 200，返回错误信息
            return {
                success: false,
                error: `请求失败，状态码: ${response.status}`,
            };
        }
    } catch (error) {
        // 捕获请求错误
        console.error(`Request failed for ${url}:`, error);
        return {
            success: false,
            error: error.response ? error.response.data : error.message,
        };
    }
}


// 定义 API 配置对象
const apiConfig = {
    // 示例：GET 请求
    me: {
        method: 'GET',
        url: '/api/auth/me/',
        isFileUpload: false,
        requiresAuth: true
    },
    register: {
        method: 'POST',
        url: '/api/auth/register/',
        isFileUpload: true,
        fileKey: 'avatar',
        requiresAuth: false
    },
    login: {
        method: 'POST',
        url: '/api/auth/login/',
        isFileUpload: false,
        requiresAuth: false
    },
    // 文件上传API
    uploadFile: {
        method: 'POST',
        url: '/api/files/upload',
        isFileUpload: true,
        fileKey: 'file',
        requiresAuth: true
    },
    // 创建文件夹API
    createFolder: {
        method: 'POST',
        url: '/api/files/folders',
        isFileUpload: false,
        requiresAuth: true
    },
    // 获取文件列表API
    getFileList: {
        method: 'GET',
        url: '/api/files/list',
        isFileUpload: false,
        requiresAuth: true
    },
    // 模型配置相关API
    getModelConfig: {
        method: 'GET',
        url: '/api/model/config',
        requiresAuth: true
    },
    saveModelConfig: {
        method: 'POST', 
        url: '/api/model/config',
        requiresAuth: true
    },
    testModelConnection: {
        method: 'POST',
        url: '/api/model/test',
        requiresAuth: true
    },
    // 智能策略API
    getStrategy: {
        method: 'GET',
        url: '/api/strategies/:id',
        requiresAuth: true
    },
    getStrategies: {
        method: 'GET',
        url: '/api/strategies',
        requiresAuth: true
    },
    createStrategy: {
        method: 'POST',
        url: '/api/strategies',
        requiresAuth: true
    },
    updateStrategy: {
        method: 'PUT',
        url: '/api/strategies/:id',
        requiresAuth: true
    },
    exportStrategy: {
        method: 'POST',
        url: '/api/strategies/export',
        requiresAuth: true
    },
    importStrategy: {
        method: 'POST',
        url: '/api/strategies/import',
        isFileUpload: true,
        fileKey: 'strategyFile',
        requiresAuth: true
    },
  // 开发环境mock数据
  mockStrategies: {
    method: 'GET',
    url: '/api/mock/strategies',
    requiresAuth: false
  },
  // 标签管理API
  getTags: {
    method: 'GET',
    url: '/api/tags/',
    requiresAuth: true
  },
  createTag: {
    method: 'POST',
    url: '/api/tags/',
    requiresAuth: true
  },
  updateTag: {
    method: 'PUT',
    url: '/api/tags/:id/',
    requiresAuth: true
  },
  deleteTag: {
    method: 'DELETE',
    url: '/api/tags/:id/',
    requiresAuth: true
  },
    refreshToken: {
        method: 'POST',
        url: '/api/auth/refresh/',
        isFileUpload: false,
        requiresAuth: false
    }
};

// 生成 API 请求函数
function createApiMethods(config) {
    const apiMethods = {};

    Object.keys(config).forEach((apiName) => {
        const defaultConfig = {
            method: "GET",
            url: "",
            isFileUpload: false,
            fileKey: "",
            requiresAuth: true,
        }
        const finalConfig = Object.assign({}, defaultConfig, config[apiName]);
        const {method, url, isFileUpload, fileKey, requiresAuth} = finalConfig;
        apiMethods[apiName] = async (data = {}, params = {}, pathParams = {}, headers = {}, config = {}) => {
            // console.log(`api request ${apiName} from url ${url}`);
            return await request({
                method,
                url,
                data,
                params,
                pathParams,
                headers,
                isFileUpload,
                fileKey,
                requiresAuth,
                ...config
            });
        };
    });

    return apiMethods;
}

// 通过配置自动生成所有 API 方法
const apiService = createApiMethods(apiConfig);

// 将apiService挂载到instance上以便拦截器使用
instance.apiService = apiService;

export default apiService;
