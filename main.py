import os
import yaml
import numpy as np
from engine.dataset_engine import DatasetEngine
import signals 
from utils.visualizer import evaluate_and_visualize 

def main():
    config_path = 'config/default.yaml'
    if not os.path.exists(config_path):
        print(f"[!] 未找到配置文件: {config_path}")
        return
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    fs = config.get('fs', 1000) 

    print("[*] 初始化数据集引擎...")
    engine = DatasetEngine(config)
    
    print("[*] 调度引擎生成复合雷达信号环境...")
    # 引擎分发全局 STFT 配置并进行叠加，返回波形和标注[cite: 3]
    mixed_waveform, obb_labels = engine.generate_sample() 
    
    if mixed_waveform is not None:
            t = np.arange(len(mixed_waveform)) / fs
            
            # 将整个 config 传入，方便可视化器读取你配置的图像尺寸
            evaluate_and_visualize(
                t=t, 
                signal_data=mixed_waveform, 
                fs=fs, 
                signal_name="Mixed_Radar_Environment",
                obb_labels=obb_labels,
                config=config  # <--- 关键：透传 config
            )

if __name__ == '__main__':
    main()