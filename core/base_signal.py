from abc import ABC,abstractmethod

class BaseRadarSignal(ABC):
    def __init__(self, fs, duration, stft_config=None, **kwargs):
        self.fs = fs
        self.duration = duration
        
        # 引入 STFT 配置和图像配置，用于动态计算坐标和厚度
        # 如果没有传入，给一套默认值用于测试
        self.stft_config = stft_config or {
            'nperseg': 256,         # STFT 窗口长度
            'window': 'hann',       # 窗口类型
            'img_height': 640,      # 时频图的像素高度
            'f_max': fs / 2         # Y 轴最高频率 (通常是 fs/2)
        }

    def get_dynamic_thickness(self):
        """
        根据 STFT 参数动态计算 OBB 框的半厚度（像素）
        """
        nperseg = self.stft_config['nperseg']
        img_height = self.stft_config['img_height']
        f_max = self.stft_config['f_max']

        # 1. 计算汉宁窗的物理总带宽 (Hz)
        w_hz = 2.0 * (self.fs / nperseg)

        # 2. 计算像素与频率的比例尺 (Pixels / Hz)
        scale = img_height / f_max

        # 3. 计算半厚度像素值
        half_thickness_pixel = (w_hz / 2.0) * scale
        
        # 为了防止极端情况下框太细导致网络难学习，可以设置一个最小像素阈值(例如 2.0)
        return max(half_thickness_pixel, 2.0)

    @abstractmethod
    def generate_waveform(self):
        pass

    @abstractmethod
    def get_obb_box(self):
        pass

    