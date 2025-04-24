import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import VueDevTools from 'vite-plugin-vue-devtools'
import legacy from '@vitejs/plugin-legacy';

// https://vitejs.dev/config/
export default defineConfig({
    base: "./",
    plugins: [
        vue(),
        VueDevTools(),
        legacy({
            targets: ["defaults", "not IE 11"],
        })
        // ViteAliases()
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
            '@images': fileURLToPath(new URL('./src/assets/images', import.meta.url)),
            '@style': fileURLToPath(new URL('./src/style', import.meta.url)),
            '@views': fileURLToPath(new URL('./src/views', import.meta.url)),
            '@assets': fileURLToPath(new URL('./src/assets', import.meta.url)),
        }
    },
    build: {
        rollupOptions: {
            output: {
                entryFileNames: "static/js/[name]-[hash].js",
                chunkFileNames: "static/js/[name]-[hash].js",
                assetFileNames(assetInfo) {
                    if (assetInfo.name.endsWith(".css")) {
                        return "static/css/[name]-[hash].css";
                    }
                    if (assetInfo.name.endsWith(".css")) {
                        return "static/css/[name]-[hash].css";
                    }
                    const imgExtendList = ["png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".ico"]
                    if (imgExtendList.some(ext => {
                        assetInfo.name.endsWith(ext)
                    })) {
                        return "static/images/[name]-[hash].[ext]";
                    }
                    return "static/assets/[name]-[hash].[ext]";

                },
            }
        }
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,

            },
            "/static": {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
            "/media": {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            }
        }
    }
})
