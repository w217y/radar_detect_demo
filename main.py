import yaml
import warnings
warnings.filterwarnings("ignore")


import signals
from engine.dataset_engine import DatasetEngine

def main():
    print('---- 雷达信号生成引擎启动 ---')

    with open("radar_detect_demo\config\default.yaml",'r',encoding='utf-8') as f:
        config = yaml.safe_load(f)

    engine = DatasetEngine(config=config)

    engine.generate_sample()

if __name__ == '__main__':
    main()