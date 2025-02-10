import sys
import os
import yt_dlp
import subprocess
from pydub import AudioSegment
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QComboBox, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QFont, QTextCursor, QIcon
from PyQt6.QtCore import Qt, QUrl

class ClickableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setAcceptRichText(True)

    def mousePressEvent(self, event):
        pos = event.pos()
        cursor = self.cursorForPosition(pos)
        anchor = cursor.charFormat().anchorHref()
        if anchor:
            url = QUrl(anchor)
            if url.scheme() == "folder":
                path = url.path().lstrip('/')  # 移除开头的斜杠
                if os.path.exists(path):
                    if sys.platform == 'win32':
                        os.startfile(os.path.dirname(path))
                    elif sys.platform == 'darwin':
                        subprocess.run(['open', os.path.dirname(path)])
                    else:
                        subprocess.run(['xdg-open', os.path.dirname(path)])
        super().mousePressEvent(event)


class YouTubeMP3Downloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube MP3 下载器")
        self.setGeometry(200, 200, 800, 500)
        self.setFont(QFont("Microsoft YaHei UI", 10))
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                margin: 5px 0;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2473a6;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
            QComboBox:drop-down {
                border: none;
                padding-right: 20px;
            }
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        language_layout = QHBoxLayout()
        self.language_label = QLabel("语言 / Language:")
        self.language_selector = QComboBox()
        self.language_selector.addItems(["中文", "English"])
        self.language_selector.currentIndexChanged.connect(self.change_language)
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_selector)
        language_layout.addStretch()
        main_layout.addLayout(language_layout)

        url_container = QFrame()
        url_container.setStyleSheet("QFrame { background-color: white; border-radius: 8px; padding: 15px; }")
        url_layout = QVBoxLayout(url_container)
        self.label = QLabel("请输入 YouTube 视频链接：")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_layout.addWidget(self.label)
        url_layout.addWidget(self.url_input)
        main_layout.addWidget(url_container)

        output_container = QFrame()
        output_container.setStyleSheet("QFrame { background-color: white; border-radius: 8px; padding: 15px; }")
        output_layout = QVBoxLayout(output_container)

        output_header = QHBoxLayout()
        self.output_label = QLabel("输出文件夹:")
        output_header.addWidget(self.output_label)
        output_layout.addLayout(output_header)

        output_selection = QHBoxLayout()
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Export")
        self.output_display = QLineEdit(self.output_path)
        self.output_display.setReadOnly(True)

        self.browse_button = QPushButton("选择文件夹")
        self.browse_button.setMaximumWidth(120)

        self.open_folder_button = QPushButton("打开文件夹")
        self.open_folder_button.setMaximumWidth(120)

        output_selection.addWidget(self.output_display)
        output_selection.addWidget(self.browse_button)
        output_selection.addWidget(self.open_folder_button)
        output_layout.addLayout(output_selection)

        main_layout.addWidget(output_container)

        self.download_button = QPushButton("下载并转换为 MP3")
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.download_mp3)
        main_layout.addWidget(self.download_button)

        log_container = QFrame()
        log_container.setStyleSheet("QFrame { background-color: white; border-radius: 8px; padding: 15px; }")
        log_layout = QVBoxLayout(log_container)
        log_label = QLabel("下载日志:")
        self.log_output = ClickableTextEdit()
        self.log_output.setMinimumHeight(150)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_output)
        main_layout.addWidget(log_container)

        self.setLayout(main_layout)

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.ffmpeg_path = os.path.join(self.base_path, "ffmpeg.exe")
        self.ffprobe_path = os.path.join(self.base_path, "ffprobe.exe")

        AudioSegment.converter = self.ffmpeg_path
        AudioSegment.ffmpeg = self.ffmpeg_path
        AudioSegment.ffprobe = self.ffprobe_path

        self.browse_button.clicked.connect(self.select_output_folder)
        self.open_folder_button.clicked.connect(self.open_output_folder)

        self.language = "中文"
        self.update_ui_text()

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        if os.path.exists(self.output_path):
            if sys.platform == 'win32':
                os.startfile(self.output_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.output_path])
            else:  # linux
                subprocess.run(['xdg-open', self.output_path])
        else:
            self.log("❌ 输出文件夹不存在！" if self.language == "中文" else "❌ Output folder doesn't exist!")

    def log(self, message, file_path=None):
        if file_path:
            message = f"{message}"

        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
        QApplication.processEvents()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_path = folder
            self.output_display.setText(folder)

    def download_mp3(self):
        url = self.url_input.text().strip()
        if not url:
            self.log("❌ 请输入 YouTube 视频链接！" if self.language == "中文" else "❌ Please enter a YouTube video URL!")
            return

        self.download_button.setEnabled(False)
        self.download_button.setText("下载中..." if self.language == "中文" else "Downloading...")

        try:
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.output_path}/%(title)s.%(ext)s',
                'quiet': False,
                'noplaylist': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log(f"🎵 正在下载: {url}" if self.language == "中文" else f"🎵 Downloading: {url}")
                ydl.download([url])

            downloaded_files = [
                os.path.join(self.output_path, f) for f in os.listdir(self.output_path)
                if f.endswith(('.webm', '.m4a', '.mp4'))
            ]

            if not downloaded_files:
                raise Exception("No files downloaded")

            for file in downloaded_files:
                audio = AudioSegment.from_file(file)
                mp3_file = os.path.join(self.output_path, f"{os.path.splitext(os.path.basename(file))[0]}.mp3")
                audio.export(mp3_file, format="mp3", bitrate="320k", codec="libmp3lame")
                os.remove(file)

                success_msg = f"✅ {'下载成功！MP3 已保存' if self.language == '中文' else 'Download complete! MP3 saved to'}: {mp3_file}"
                self.log(success_msg, mp3_file)

        except Exception as e:
            self.log(f"⚠️ 错误: {str(e)}" if self.language == "中文" else f"⚠️ Error: {str(e)}")

        finally:
            self.download_button.setEnabled(True)
            self.download_button.setText("下载并转换为 MP3" if self.language == "中文" else "Download & Convert to MP3")

    def change_language(self):
        self.language = self.language_selector.currentText()
        self.update_ui_text()

    def update_ui_text(self):
        if self.language == "中文":
            self.setWindowTitle("YouTube MP3 下载器")
            self.language_label.setText("语言 / Language:")
            self.label.setText("请输入 YouTube 视频链接：")
            self.output_label.setText("输出文件夹:")
            self.browse_button.setText("选择文件夹")
            self.open_folder_button.setText("打开文件夹")
            self.download_button.setText("下载并转换为 MP3")
        else:
            self.setWindowTitle("YouTube MP3 Downloader")
            self.language_label.setText("Language / 语言:")
            self.label.setText("Enter YouTube Video URL:")
            self.output_label.setText("Output Folder:")
            self.browse_button.setText("Select Folder")
            self.open_folder_button.setText("Open Folder")
            self.download_button.setText("Download & Convert to MP3")


def main():
    app = QApplication(sys.argv)
    window = YouTubeMP3Downloader()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
