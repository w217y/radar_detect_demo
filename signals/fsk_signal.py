import numpy as np
from core.registry import SignalRegistry
from core.base_signal import BaseRadarSignal

@SignalRegistry.register("FSK")
class FSKSignal(BaseRadarSignal):
    def __init__(self, fs, duration, hop_frequencies, hop_duration, stft_config=None):
        super().__init__(fs, duration, stft_config)
        self.hop_frequencies = hop_frequencies
        self.hop_duration = hop_duration

    def generate_waveform(self):
        t_total = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        waveform = np.zeros_like(t_total)
        samples_per_hop = int(self.fs * self.hop_duration)
        
        # 将不同频率的正弦波按时间段拼接到一起
        for i, freq in enumerate(self.hop_frequencies):
            start_idx = i * samples_per_hop
            end_idx = min((i + 1) * samples_per_hop, len(t_total))
            t_segment = t_total[start_idx:end_idx]
            waveform[start_idx:end_idx] = np.cos(2 * np.pi * freq * t_segment)
            
        return waveform

    def get_obb_box(self):
        # 1. 解析全局配置
        img_width = self.stft_config['img_width']
        scale_y = self.stft_config['img_height'] / self.stft_config['f_max']
        
        # X轴的比例尺：像素/秒
        scale_x = img_width / self.duration 
        
        # 2. 获取物理动态厚度
        thickness = self.get_dynamic_thickness()
        
        obb_boxes = []
        
        # 3. 遍历每个频率跳变段，计算对应的短横线 OBB
        for i, freq in enumerate(self.hop_frequencies):
            # 物理时间
            start_time = i * self.hop_duration
            end_time = (i + 1) * self.hop_duration
            
            # 映射为 X 像素
            x_start = start_time * scale_x
            x_end = end_time * scale_x
            
            # 映射为 Y 像素
            y_center = freq * scale_y
            
            x1, y1 = x_start, y_center - thickness
            x2, y2 = x_end,   y_center - thickness
            x3, y3 = x_end,   y_center + thickness
            x4, y4 = x_start, y_center + thickness
            
            obb_boxes.append([x1, y1, x2, y2, x3, y3, x4, y4])
            
        return obb_boxes