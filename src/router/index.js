import {createRouter, createWebHistory} from 'vue-router'


const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: []
})


router.beforeEach((to, from, next) => {
    // 如果目标路由需要登录

    if (to.name === "Home") {
        next({name: 'HomeIndex'});
        return
    }
    if (to.name === "system_home") {
        next({name: 'DataSetView'});
        return
    }
    if (to.matched.some(record => record.meta.requiresAuth)) {
        // 判断用户是否已登录（这里使用 localStorage 判断登录状态）
        const isLoggedIn = localStorage.getItem('access');  // 检查access token

        if (!isLoggedIn) {
            // 如果未登录，跳转到登录页面
            next({name: 'HomeIndex'});
        } else {
            // 如果已登录，继续访问目标页面
            next();
        }
    } else {
        // 不需要登录的页面直接访问
        next();
    }
});

export default router
