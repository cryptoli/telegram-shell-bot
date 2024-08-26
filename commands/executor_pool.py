from concurrent.futures import ThreadPoolExecutor

# 全局线程池实例
executor = ThreadPoolExecutor(max_workers=5)  # 根据需求调整线程池大小

def submit_task(func, *args, **kwargs):
    """
    提交任务到线程池执行。
    
    :param func: 要执行的函数
    :param args: 函数的参数
    :param kwargs: 函数的关键字参数
    :return: Future 对象
    """
    return executor.submit(func, *args, **kwargs)

def shutdown_executor():
    """
    关闭线程池，在不再需要时调用。
    """
    executor.shutdown(wait=True)

