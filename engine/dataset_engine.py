from core.registry import SignalRegistry

class DatasetEngine:
    def __init__(self, config):
        self.config = config
        # 提取全局 STFT 配置
        self.stft_config = config.get('stft_config', {})

    def generate_sample(self):
        print("\n>>> [Engine] 开始调度，分发全局 STFT 配置...")
        mixed_waveform = 0
        obb_labels = []

        for sig_config in self.config.get('signals', []):
            sig_type = sig_config['type']
            sig_params = sig_config['params']
            
            # 【关键动作】：将全局 STFT 配置注入到该信号的参数中
            sig_params['stft_config'] = self.stft_config
            
            SignalClass = SignalRegistry.get_signal_class(sig_type)
            signal_instance = SignalClass(**sig_params)
            
            # 时域波形叠加
            mixed_waveform += signal_instance.generate_waveform()
            
            # 收集并展平 OBB 框
            boxes = signal_instance.get_obb_box()
            for box in boxes:
                obb_labels.append({"class": sig_type, "bbox": box})

        print("\n<<< [Engine] 样本生成完毕！")
        print(f"<<< [Engine] 汇总的 OBB 标签数据: {obb_labels}\n")
        
        return mixed_waveform, obb_labels