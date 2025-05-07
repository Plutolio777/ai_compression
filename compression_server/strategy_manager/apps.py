# strategy_manager/apps.py
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
import atexit
import logging

logger = logging.getLogger(__name__)
# 1. 初始化调度器
scheduler = BackgroundScheduler()

class StrategyManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'strategy_manager'
    _scheduler_started = False  # 类变量防止重复启动

    def ready(self):
        """Django启动时自动调用"""
        if not self._scheduler_started and self._should_start_scheduler():
            self._start_scheduler()

    def _should_start_scheduler(self):
        """判断是否应该启动调度器"""
        # 开发环境下runserver会启动两个进程，只需要在主进程中启动
        return os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('DJANGO_SETTINGS_MODULE')

    def _start_scheduler(self):
        """启动调度器并添加任务"""
        try:
            logger.info("正在初始化任务调度器...")
            
            # 2. 从数据库加载策略并创建任务
            self._load_strategies(scheduler)
            print(11111)
            # 3. 启动调度器
            scheduler.start()
            StrategyManagerConfig._scheduler_started = True
            
            # 4. 注册退出时的清理函数
            atexit.register(lambda: scheduler.shutdown())
            
            logger.info("任务调度器启动完成")
        except Exception as e:
            logger.error(f"启动调度器失败: {e}", exc_info=True)

    def _load_strategies(self, scheduler):
        """从数据库加载策略并创建定时任务"""
        from .models import Strategy  # 延迟导入避免循环引用
        
        strategies = Strategy.objects.all()
        if not strategies.exists():
            print("没有找到任何策略配置")
            return
            
        for strategy in strategies:
            print("开始处理策略:", strategy, strategy.config)
            try:
                self._add_strategy_job(scheduler, strategy)
                print(f"已添加策略任务: {strategy.id}")
            except Exception as e:
                print(f"添加策略任务失败(ID:{strategy.id}): {e}")

    def _add_strategy_job(self, scheduler, strategy):
        """为单个策略添加任务"""
        # 从策略配置中解析定时规则
        trigger = self._parse_trigger(strategy.config)
        
        # 添加任务到调度器
        scheduler.add_job(
            self._execute_strategy,  # 任务执行函数
            trigger=trigger,
            id=f'strategy_{strategy.id}',
            args=[strategy.id],  # 传递给执行函数的参数
            max_instances=1,
            replace_existing=True
        )

    def _parse_trigger(self, config):
        from apscheduler.triggers.interval import IntervalTrigger  # 新增导入
        archive_config = config.get('archive', {})
        period = int(archive_config.get('period', 1))
        unit = archive_config.get('unit', 'minutes')  # 默认分钟
        
        units = {
            'minutes': ('minutes', 1, 60*24*365),
            'hours': ('hours', 1, 24*365),
            'days': ('days', 1, 365)
        }
        
        if unit not in units:
            unit = 'minutes'
        
        unit_name, min_val, max_val = units[unit]
        period = max(min_val, min(period, max_val))
        
        return IntervalTrigger(**{unit_name: period})

    def _execute_strategy(self, strategy_id):
        """实际执行策略任务"""
        from .models import Strategy
        try:
            strategy = Strategy.objects.get(id=strategy_id)
            logger.info(f"正在执行策略: {strategy.id}")
            # 这里添加实际的策略执行逻辑
            # ...
        except Exception as e:
            logger.error(f"执行策略失败(ID:{strategy_id}): {e}")