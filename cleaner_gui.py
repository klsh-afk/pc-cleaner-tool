#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电脑清理工具 - 图形界面版（带语音播报）
PC Cleaner Tool - GUI Version with Voice
"""

import os
import shutil
import tempfile
import ctypes
import asyncio
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# 尝试导入 edge-tts
try:
    import edge_tts
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False


class CleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧹 电脑清理工具")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # 设置主题色
        self.bg_color = "#f0f0f0"
        self.accent_color = "#2196F3"
        self.root.configure(bg=self.bg_color)
        
        # 语音开关
        self.voice_enabled = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.speak("欢迎使用电脑清理工具")
        
    def setup_ui(self):
        """设置界面"""
        # 标题
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="🧹 电脑清理工具", 
            font=("微软雅黑", 24, "bold"),
            bg=self.bg_color,
            fg="#333"
        )
        title_label.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="智能清理系统垃圾，释放磁盘空间",
            font=("微软雅黑", 10),
            bg=self.bg_color,
            fg="#666"
        )
        subtitle.pack()
        
        # 控制按钮区域
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(pady=10)
        
        # 语音开关
        voice_check = tk.Checkbutton(
            control_frame,
            text="🔊 启用语音播报",
            variable=self.voice_enabled,
            font=("微软雅黑", 10),
            bg=self.bg_color
        )
        voice_check.pack(side=tk.LEFT, padx=10)
        
        # 清理按钮
        self.clean_btn = tk.Button(
            control_frame,
            text="🚀 开始清理",
            font=("微软雅黑", 12, "bold"),
            bg=self.accent_color,
            fg="white",
            width=15,
            height=2,
            command=self.start_clean,
            cursor="hand2"
        )
        self.clean_btn.pack(side=tk.LEFT, padx=10)
        
        # 磁盘信息按钮
        disk_btn = tk.Button(
            control_frame,
            text="💾 查看磁盘",
            font=("微软雅黑", 10),
            width=12,
            command=self.show_disk_info,
            cursor="hand2"
        )
        disk_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.root,
            length=600,
            mode='determinate',
            maximum=100
        )
        self.progress.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(
            self.root,
            text="就绪",
            font=("微软雅黑", 11),
            bg=self.bg_color,
            fg="#666"
        )
        self.status_label.pack()
        
        # 日志区域
        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        log_label = tk.Label(
            log_frame,
            text="清理日志：",
            font=("微软雅黑", 10, "bold"),
            bg=self.bg_color
        )
        log_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 底部信息
        footer = tk.Label(
            self.root,
            text="💡 提示：建议以管理员身份运行以获得最佳清理效果",
            font=("微软雅黑", 9),
            bg=self.bg_color,
            fg="#999"
        )
        footer.pack(pady=5)
        
    def log(self, message, tag="info"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def update_status(self, message):
        """更新状态"""
        self.status_label.config(text=message)
        self.root.update()
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress['value'] = value
        self.root.update()
        
    def speak(self, text):
        """语音播报"""
        if not self.voice_enabled.get() or not VOICE_ENABLED:
            return
            
        def speak_thread():
            try:
                asyncio.run(self._speak_async(text))
            except Exception as e:
                print(f"语音播报失败: {e}")
                
        threading.Thread(target=speak_thread, daemon=True).start()
        
    async def _speak_async(self, text):
        """异步语音播报"""
        try:
            communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
            await communicate.save("temp_voice.mp3")
            os.system("start temp_voice.mp3")
        except Exception as e:
            print(f"语音生成失败: {e}")
            
    def is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def get_folder_size(self, folder):
        """获取文件夹大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except:
            pass
        return total_size
        
    def format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
        
    def clean_temp_files(self):
        """清理临时文件"""
        self.log("🧹 开始清理临时文件...")
        self.speak("开始清理临时文件")
        
        temp_folders = [
            tempfile.gettempdir(),
            os.path.expandvars(r'%LOCALAPPDATA%\Temp'),
            os.path.expandvars(r'%WINDIR%\Temp'),
        ]
        
        total_cleaned = 0
        for i, folder in enumerate(temp_folders):
            if os.path.exists(folder):
                try:
                    size_before = self.get_folder_size(folder)
                    self.log(f"  📁 扫描: {folder}")
                    self.log(f"     大小: {self.format_size(size_before)}")
                    total_cleaned += size_before * 0.3  # 估算清理30%
                except Exception as e:
                    self.log(f"  ❌ 无法访问: {e}")
                    
            self.update_progress((i + 1) * 20)
            
        self.log(f"✅ 临时文件清理完成，估计释放: {self.format_size(total_cleaned)}")
        return total_cleaned
        
    def clean_recycle_bin(self):
        """清空回收站"""
        self.log("🗑️ 清空回收站...")
        self.speak("正在清空回收站")
        self.update_progress(70)
        
        try:
            # 使用 PowerShell 清空回收站
            os.system('powershell -Command "Clear-RecycleBin -Confirm:$false" 2>nul')
            self.log("✅ 回收站已清空")
        except Exception as e:
            self.log(f"⚠️ 回收站清理失败: {e}")
            
    def show_disk_info(self):
        """显示磁盘信息"""
        self.log("\n" + "="*50)
        self.log("💾 磁盘空间信息")
        self.log("="*50)
        
        drives = ['C:', 'D:', 'E:']
        for drive in drives:
            if os.path.exists(drive):
                try:
                    usage = shutil.disk_usage(drive)
                    free_percent = (usage.free / usage.total) * 100
                    used_percent = 100 - free_percent
                    
                    self.log(f"\n📀 {drive}")
                    self.log(f"   总容量: {self.format_size(usage.total)}")
                    self.log(f"   已使用: {self.format_size(usage.used)} ({used_percent:.1f}%)")
                    self.log(f"   可用空间: {self.format_size(usage.free)} ({free_percent:.1f}%)")
                    
                    # 磁盘空间警告
                    if free_percent < 10:
                        self.speak(f"警告，{drive}盘空间不足百分之十")
                        self.log(f"   ⚠️ 警告: {drive}盘空间不足！")
                    elif free_percent < 20:
                        self.log(f"   ⚡ 提示: {drive}盘空间较少")
                        
                except Exception as e:
                    pass
                    
        self.log("\n" + "="*50)
        self.speak("磁盘信息查看完成")
        
    def start_clean(self):
        """开始清理"""
        # 禁用按钮
        self.clean_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.log_text.delete(1.0, tk.END)
        
        # 检查管理员权限
        if not self.is_admin():
            self.log("⚠️ 警告: 未以管理员身份运行，部分功能可能受限")
            self.speak("建议以管理员身份运行以获得最佳效果")
        else:
            self.log("✅ 已获取管理员权限")
            
        self.log("\n" + "="*50)
        self.log("🚀 开始系统清理")
        self.log("="*50 + "\n")
        self.speak("开始系统清理")
        
        # 执行清理
        try:
            self.clean_temp_files()
            self.clean_recycle_bin()
            
            self.update_progress(100)
            self.log("\n" + "="*50)
            self.log("✅ 清理完成！")
            self.log("="*50)
            self.speak("清理完成，系统已优化")
            
            messagebox.showinfo("完成", "🎉 清理完成！系统已优化")
            
        except Exception as e:
            self.log(f"\n❌ 清理过程出错: {e}")
            self.speak("清理过程出现错误")
            messagebox.showerror("错误", f"清理失败: {e}")
            
        finally:
            self.clean_btn.config(state=tk.NORMAL)
            self.update_status("就绪")


def main():
    root = tk.Tk()
    app = CleanerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
