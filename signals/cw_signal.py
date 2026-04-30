import numpy as np
from core.registry import SignalRegistry
from core.base_signal import BaseRadarSignal

@SignalRegistry.register("CW")
class CWSignal(BaseRadarSignal):
    def __init__(self, fs, duration, fc, stft_config=None):
        super().__init__(fs, duration, stft_config)
        self.fc = fc

    def generate_waveform(self):
        t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        return np.cos(2 * np.pi * self.fc * t)

    def get_obb_box(self):
        # 1. 获取图像宽度映射 (假设 1 秒映射到 640 像素宽度)
        # 实际项目中，这也应该从 stft_config 推导，这里为了演示简化
        img_width = 640 
        x_start, x_end = 0.0, float(img_width)
        
        # 2. 计算中心频率的 Y 坐标映射
        scale = self.stft_config['img_height'] / self.stft_config['f_max']
        y_center = self.fc * scale
        
        # 3. 调用基类方法获取由物理公式推导出的真实半厚度！
        thickness = self.get_dynamic_thickness()
        
        x1, y1 = x_start, y_center - thickness
        x2, y2 = x_end,   y_center - thickness
        x3, y3 = x_end,   y_center + thickness
        x4, y4 = x_start, y_center + thickness
        
        return [[x1, y1, x2, y2, x3, y3, x4, y4]]