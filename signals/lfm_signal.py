import numpy as np
from core.registry import SignalRegistry
from core.base_signal import BaseRadarSignal

@SignalRegistry.register("LFM")
class LFMSignal(BaseRadarSignal):
    def __init__(self, fs, duration, f0, f1, stft_config=None):
        super().__init__(fs, duration, stft_config)
        self.f0 = f0
        self.f1 = f1

    def generate_waveform(self):
        t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        k = (self.f1 - self.f0) / self.duration
        return np.cos(2 * np.pi * (self.f0 * t + 0.5 * k * t**2))

    def get_obb_box(self):
        # 1. 解析全局配置
        img_width = self.stft_config['img_width']
        scale_y = self.stft_config['img_height'] / self.stft_config['f_max']
        
        # 2. X轴映射 (起始到结束)
        x_start, x_end = 0.0, float(img_width)
        
        # 3. Y轴映射 (根据频率)
        y_start = self.f0 * scale_y
        y_end = self.f1 * scale_y
        
        # 4. 获取物理动态厚度
        thickness = self.get_dynamic_thickness()
        
        # 5. 计算倾斜矩形的四个顶点
        x1, y1 = x_start, y_start - thickness  # 左上
        x2, y2 = x_end,   y_end - thickness    # 右上
        x3, y3 = x_end,   y_end + thickness    # 右下
        x4, y4 = x_start, y_start + thickness  # 左下
        
        return [[x1, y1, x2, y2, x3, y3, x4, y4]]