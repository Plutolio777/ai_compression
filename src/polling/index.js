import {onBeforeUnmount, ref} from 'vue';

export function useMultipleTaskPolling({
                                           executeTaskFn,            // 执行任务接口
                                           fetchTaskProgressFn,      // 获取任务进度接口
                                           interval = 1000           // 轮询间隔
                                       }) {
    const tasks = ref([]);     // 存储任务的数组

    // 执行任务方法
    const executeTask = async (sourceTask) => {
        try {
            console.log(tasks.value)
            // 执行任务接口下发任务
            const response = await executeTaskFn(sourceTask);
            const taskId = sourceTask.id // response.data.taskId;

            // 每个任务都有自己的状态
            const task = {
                taskId,
                isLoading: true,
                isComplete: false,
                error: null,
                intervalId: null,
                lastFetchTime: 0,
                obj: sourceTask,
            };


            tasks.value.push(task);
        } catch (err) {
            console.error('执行任务失败', err);
        }
    };

    // 轮询任务进度
    const fetchTaskProgress = async (task) => {
        // 节流机制，防止请求时间过长
        console.log(task)
        const currentTime = Date.now();
        if (currentTime - task.lastFetchTime < interval) {
            return; // 如果距离上次请求时间太短，则跳过这次请求
        }

        task.lastFetchTime = currentTime;

        try {
            const response = await fetchTaskProgressFn(task.taskId);

            // if (response.data.status === 'complete') {
            //     task.isComplete = true;  // 任务完成
            //     stopPolling(task);  // 停止该任务的轮询
            // }
            //
            // // 在这里修改任务数据
            // task.isLoading = false; // 完成了请求，可以更新任务的加载状态
        } catch (err) {
            task.error = '获取任务进度失败';
        }
    };

    // 启动任务轮询
    const startPolling = (task) => {
        task.intervalId = setInterval(() => {
            fetchTaskProgress(task);
        }, interval);
    };

    // 停止任务轮询
    const stopPolling = (task) => {
        clearInterval(task.intervalId);
        task.intervalId = null;
    };

    // 在组件销毁前停止所有任务的轮询
    onBeforeUnmount(() => {
        tasks.value.forEach(stopPolling);
    });

    return {
        tasks,               // 返回所有任务的状态
        executeTask,         // 允许手动触发任务执行
    };
}
