import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import matplotlib.patches as patches
import math

def evaluate_and_visualize(t, signal_data, fs, signal_name="Mixed_Radar_Environment", obb_labels=None, config=None):
    is_complex = np.iscomplexobj(signal_data)
    plot_data = np.real(signal_data) if is_complex else signal_data

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(f'Visual Evaluation: {signal_name}', fontsize=16, fontweight='bold')
    duration = len(signal_data) / fs
    max_freq = fs / 2

    # 1. 时域波形
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.plot(t, plot_data, color='#1f77b4', linewidth=1)
    ax1.set_title('Time Domain Waveform')
    ax1.set_xlim([0, duration])
    ax1.grid(True)

    # 2. 频域频谱 (FFT)
    ax2 = fig.add_subplot(3, 1, 2)
    n = len(signal_data)
    freqs = np.fft.fftshift(np.fft.fftfreq(n, d=1/fs))
    fft_values = np.fft.fftshift(np.abs(np.fft.fft(signal_data)))
    ax2.plot(freqs, 20 * np.log10(fft_values + 1e-10), color='#2ca02c')
    ax2.set_title('Frequency Spectrum (FFT)')
    ax2.grid(True)

    # 3. 时频分布 (STFT) 
    ax3 = fig.add_subplot(3, 1, 3)
    nperseg_viz = min(256, max(16, len(signal_data) // 8))
    noverlap_viz = nperseg_viz - max(1, nperseg_viz // 10) 
    f, t_stft, Sxx = spectrogram(plot_data, fs, nperseg=nperseg_viz, noverlap=noverlap_viz)
    
    # 强制使底图完全对齐物理坐标 [0~duration, 0~fs/2]
    img_extent = [0, duration, 0, max_freq]
    cax = ax3.imshow(10 * np.log10(Sxx + 1e-10), aspect='auto', origin='lower', extent=img_extent, cmap='viridis')
    ax3.set_title('Time-Frequency Distribution (STFT) with True Physical Alignment')
    ax3.set_xlim([0, duration])
    ax3.set_ylim([0, max_freq])
    fig.colorbar(cax, ax=ax3, label='Power (dB)')

    # ================= 核心修复：像素坐标 -> 物理坐标的绝对映射 =================
    if obb_labels:
        color_map = {'LFM': 'red', 'FSK': 'cyan', 'CW': 'magenta'}
        
        # 目标检测网络常用输出尺寸，如果没有配置默认使用逆向推导出的 640
        img_w = config.get('img_width', 640) if config else 640
        img_h = config.get('img_height', 640) if config else 640
        
        for label in obb_labels:
            sig_class = label.get('class', 'Unknown')
            bbox = label.get('bbox')
            color = color_map.get(sig_class, 'white')
            
            if bbox is None: continue
                
            corners = []
            if len(bbox) == 5: 
                cx, cy, w, h, angle = bbox
                dx_dy = np.array([[-w/2, -h/2], [w/2, -h/2], [w/2, h/2], [-w/2, h/2]])
                cos_a, sin_a = math.cos(angle), math.sin(angle)
                rot_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
                corners = np.dot(dx_dy, rot_matrix.T) + [cx, cy]
            elif len(bbox) == 8: 
                corners = np.array(bbox).reshape(4, 2)
            elif isinstance(bbox, (list, np.ndarray)) and len(bbox) == 4:
                corners = np.array(bbox)

            if len(corners) > 0:
                # 修复 1：X 轴从 [0, 640] 像素等比例映射到 [0, 1.0] 秒
                corners[:, 0] = (corners[:, 0] / img_w) * duration
                
                # 修复 2：Y 轴从 [0, 640] 像素等比例映射到 [0, 500] 赫兹
                corners[:, 1] = (corners[:, 1] / img_h) * max_freq
                
                polygon = patches.Polygon(corners, closed=True, edgecolor=color, facecolor='none', 
                                          linewidth=2, alpha=0.8, clip_on=True)
                ax3.add_patch(polygon)
                ax3.text(corners[0][0], corners[0][1], sig_class, color='white', fontsize=9, 
                         bbox=dict(facecolor=color, alpha=0.6, edgecolor='none', pad=1), clip_on=True)
    # =========================================================

    plt.tight_layout()
    os.makedirs('output', exist_ok=True)
    save_path = f"output/{signal_name}_evaluation.png"
    plt.savefig(save_path, dpi=300)
    print(f"[*] 已保存带有精准对齐 OBB 标注的评估图表至: {save_path}")
    plt.show()
    plt.close(fig)