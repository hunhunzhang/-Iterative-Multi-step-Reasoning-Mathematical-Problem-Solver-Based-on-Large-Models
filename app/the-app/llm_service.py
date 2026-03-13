import requests
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer

class LLMWorker(QObject):
    """
    在独立线程中运行的LLM API请求工作器
    """
    response_received = pyqtSignal(str, dict)  # (response, metrics)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key, base_url, system_prompt, user_message, temperature):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.system_prompt = system_prompt
        self.user_message = user_message
        self.temperature = temperature

    def run(self):
        start_time = time.time()
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.user_message}
                ],
                "temperature": self.temperature,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()  

            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # 计算指标
            end_time = time.time()
            current_time = end_time - start_time
            
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            # 计算当前花费
            current_cost = (prompt_tokens * 2 / 1e6) + (completion_tokens * 8 / 1e6)
            
            metrics = {
                "current_prompt_tokens": prompt_tokens,
                "current_completion_tokens": completion_tokens,
                "current_total_tokens": total_tokens,
                "current_cost": current_cost,
                "current_time": current_time
            }
            
            self.response_received.emit(content, metrics)
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"网络请求错误: {e}")
        except Exception as e:
            self.error_occurred.emit(f"处理时发生未知错误: {e}")

class DeepSeekService(QObject):
    """
    用于与DeepSeek API交互的服务
    """
    iteration_complete = pyqtSignal(str, bool, dict)  # (response, is_final, metrics)
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.thread = None
        self.worker = None
        
        # 循环状态
        self.current_iteration = 0
        self.max_iterations = 50
        self.original_question = ""
        self.last_response = ""
        self.api_key = ""
        self.base_url = ""
        self.system_prompt = ""
        self.temperature = 0.7

        # 总计指标
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_time = 0.0
        self.start_time = None
        
        # 用于延迟下次调用的定时器
        self.next_call_timer = QTimer()
        self.next_call_timer.setSingleShot(True)
        self.next_call_timer.timeout.connect(self._make_api_call)
        
    def start_iterative_response(self, api_key, base_url, system_prompt, user_message, temperature=0.7, max_iterations=50):
        """开始循环调用API直到获得最终答案"""
        # 如果已有正在运行的线程，先停止它
        self._cleanup_thread()
        
        self.api_key = api_key
        self.base_url = base_url
        self.system_prompt = system_prompt
        self.original_question = user_message
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.last_response = ""
        
        # 重置总计指标
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_time = 0.0
        self.start_time = time.time()
        
        # 开始第一次调用
        self._make_api_call()
        
    def _make_api_call(self):
        """执行单次API调用"""
        # 构建当前的用户消息
        if self.last_response == "":
            current_message = self.original_question
        else:
            current_message = f"{self.original_question}\n{self.last_response}"
            
        # 创建新的线程和工作器
        self.thread = QThread()
        self.worker = LLMWorker(
            self.api_key, 
            self.base_url, 
            self.system_prompt, 
            current_message, 
            self.temperature
        )
        self.worker.moveToThread(self.thread)
        
        # 连接信号
        self.thread.started.connect(self.worker.run)
        self.worker.response_received.connect(self._handle_response)
        self.worker.error_occurred.connect(self._handle_error)
        
        # 确保线程正确清理
        self.worker.response_received.connect(self.thread.quit)
        self.worker.error_occurred.connect(self.thread.quit)
        self.thread.finished.connect(self._on_thread_finished)
        
        self.thread.start()
        
    def _on_thread_finished(self):
        """线程完成后的清理"""
        if self.thread:
            self.thread.deleteLater()
            self.thread = None
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
        
    def _handle_response(self, response, current_metrics):
        """处理API响应"""
        self.current_iteration += 1
        
        # 更新总计指标
        self.total_prompt_tokens += current_metrics["current_prompt_tokens"]
        self.total_completion_tokens += current_metrics["current_completion_tokens"]
        self.total_tokens += current_metrics["current_total_tokens"]
        self.total_cost += current_metrics["current_cost"]
        self.total_time = time.time() - self.start_time
        
        # 构建完整的指标数据
        metrics = {
            "current_prompt_tokens": current_metrics["current_prompt_tokens"],
            "current_completion_tokens": current_metrics["current_completion_tokens"],
            "current_total_tokens": current_metrics["current_total_tokens"],
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "current_cost": current_metrics["current_cost"],
            "total_cost": self.total_cost,
            "current_time": current_metrics["current_time"],
            "total_time": self.total_time
        }
        
        # 检查是否包含最终答案
        is_final = "<answer>" in response
        
        # 发送迭代完成信号
        self.iteration_complete.emit(response, is_final, metrics)
        
        # 如果不是最终答案且未达到最大迭代次数，继续下一次迭代
        if not is_final and self.current_iteration < self.max_iterations:
            self.last_response = response
            # 使用定时器延迟下次调用，确保当前线程完全清理
            self.next_call_timer.start(500)  # 500ms 延迟
        elif not is_final:
            # 达到最大迭代次数但仍未获得最终答案
            self.iteration_complete.emit("达到最大迭代次数，未能获得最终答案。", True, metrics)
            
    def _handle_error(self, error):
        """处理API错误"""
        # 创建空的指标数据
        metrics = {
            "current_prompt_tokens": 0,
            "current_completion_tokens": 0,
            "current_total_tokens": 0,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "current_cost": 0.0,
            "total_cost": self.total_cost,
            "current_time": 0.0,
            "total_time": time.time() - self.start_time if self.start_time else 0.0
        }
        self.iteration_complete.emit(f"API调用错误: {error}", True, metrics)
        
    def _cleanup_thread(self):
        """清理现有的线程和工作器"""
        # 停止定时器
        self.next_call_timer.stop()
        
        # 安全地清理线程
        if self.thread is not None:
            try:
                if self.thread.isRunning():
                    self.thread.quit()
                    if not self.thread.wait(3000):  # 等待最多3秒
                        self.thread.terminate()
                        self.thread.wait(1000)
            except RuntimeError:
                # 线程对象已被删除，忽略错误
                pass
            finally:
                self.thread = None
                
        # 清理 worker
        if self.worker is not None:
            try:
                self.worker.deleteLater()
            except RuntimeError:
                # worker 对象已被删除，忽略错误
                pass
            finally:
                self.worker = None
        
    def stop_iteration(self):
        """停止当前的迭代过程"""
        self.next_call_timer.stop()
        self._cleanup_thread()
        
    def __del__(self):
        """析构函数，确保资源正确清理"""
        self.stop_iteration()