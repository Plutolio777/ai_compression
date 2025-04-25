# API服务使用指南

## 概述

`apiService.js` 是基于axios封装的API请求服务，提供统一的请求处理、认证管理和文件上传功能。

## 核心功能

1. 自动处理认证令牌
2. 支持文件上传
3. 统一错误处理
4. 自动生成API方法

## 基本使用

### 1. 添加API配置

在`apiConfig`对象中添加API配置：

```javascript
const apiConfig = {
  getUserInfo: {
    method: 'GET',
    url: '/api/user/:id',  // 支持路径参数
    requiresAuth: true    // 需要认证
  },
  uploadFile: {
    method: 'POST',
    url: '/api/upload',
    isFileUpload: true,
    fileKey: 'file'      // 文件字段名
  }
}
```

### 2. 调用API方法

配置后会自动生成对应方法：

```javascript
// 调用用户信息接口
const result = await apiService.getUserInfo(
  {}, // 请求体数据
  {}, // 查询参数
  {id: 123} // 路径参数
);

// 调用文件上传接口
const file = document.querySelector('input[type=file]').files[0];
const uploadResult = await apiService.uploadFile(
  {file: file, description: '测试文件'}
);
```

## 配置参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| method | string | HTTP方法 (GET/POST/PUT/DELETE) |
| url | string | 接口URL，支持`:param`路径参数 |
| isFileUpload | boolean | 是否文件上传 |
| fileKey | string | 文件字段名 |
| requiresAuth | boolean | 是否需要认证 |

## 返回值格式

```typescript
interface ApiResponse {
  success: boolean;
  data?: any;      // 成功时返回的数据
  error?: string;  // 错误信息
}
```

## 注意事项

1. 文件上传时：
   - 设置`isFileUpload: true`
   - 指定`fileKey`为文件字段名
   - 支持单个文件或文件数组

2. 认证相关：
   - 需要认证的接口设置`requiresAuth: true`
   - 会自动从Vuex store获取token

3. 错误处理：
   - 所有错误会被捕获并返回统一格式
   - 建议在业务层检查`success`字段

4. 路径参数：
   - 在URL中使用`:param`格式
   - 通过`pathParams`参数传递

## 最佳实践

1. 按模块组织API配置
2. 对常用API添加类型定义
3. 在Vue组件中使用async/await处理异步
4. 统一处理错误提示
