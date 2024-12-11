import yt_dlp
import os
from pydub import AudioSegment

# 设置 LAME 编码器路径（确保 LAME 已正确安装并在系统路径中）
# 在虚拟环境中使用正确的 ffmpeg 路径
AudioSegment.converter = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
AudioSegment.ffmpeg = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffprobe.exe"

# 你可以继续运行下载和转换的代码
def download_youtube_as_mp3(url, output_path="你记得改"):
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # 配置 yt-dlp 只下载音频，不进行格式转换
    ydl_opts = {
        'format': 'bestaudio/best',  # 选择最佳音频格式
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # 设置输出路径和文件名
        'quiet': False,  # 输出详细信息，设为True会隐藏所有日志
        'noplaylist': False,  # 确保可以处理播放列表
    }

    # 使用 yt-dlp 下载音频
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"正在下载: {url}")
        ydl.download([url])

    # 获取下载的所有文件
    download_files = []
    for file in os.listdir(output_path):
        if file.endswith('.webm') or file.endswith('.m4a') or file.endswith('.mp4'):  # 添加更多音频格式检查
            download_files.append(os.path.join(output_path, file))

    if not download_files:
        print("下载失败")
        return

    # 将下载的音频文件转换为 MP3
    for download_file in download_files:
        try:
            # 使用 pydub 加载音频文件
            audio = AudioSegment.from_file(download_file)

            # 设置输出的MP3文件路径
            output_mp3 = os.path.join(output_path, f'{os.path.splitext(os.path.basename(download_file))[0]}.mp3')

            # 使用 LAME 编码器导出为 320kbps 的 MP3
            audio.export(output_mp3, format="mp3", bitrate="320k", codec="libmp3lame")

            # 删除原始下载的文件（可选）
            os.remove(download_file)

            print(f"转换成功！MP3文件已保存至：{output_mp3}")

        except Exception as e:
            print(f"转换过程中发生错误: {e}")

# 主循环，允许用户重复输入URL进行下载和转换
def main():
    while True:
        # 提示用户输入YouTube视频URL
        url = input("请输入YouTube视频URL（或输入 '退出' 来结束程序）：")
        
        # 如果用户输入 '退出'，则结束循环
        if url.lower() == '退出':
            print("退出程序")
            break
        
        # 调用下载并转换音频的函数
        download_youtube_as_mp3(url)

        # 提示用户是否继续下载
        continue_choice = input("是否继续下载其他视频？（yes/no）：").strip().lower()
        if continue_choice != 'yes':
            print("程序结束")
            break

# 运行主函数
if __name__ == "__main__":
    main()
